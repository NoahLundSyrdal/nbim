import pandas as pd
from pathlib import Path
from recon_loader import load_and_align  
from recon_breaks import classify_breaks
from fx_market_agent import verify_fx_with_intelligence
from insights_agent import generate_business_summary
import os

def compute_deterministic_analysis(merged_df):
    """Everything computable without LLM"""
    breaks = classify_breaks(merged_df)
    
    # Enhanced cash impact calculation
    breaks['cash_impact'] = breaks.apply(
        lambda r: max(abs(float(r.get('gross_nbim', 0) or 0) - float(r.get('gross_cust', 0) or 0)), 
                     abs(float(r.get('net_nbim', 0) or 0) - float(r.get('net_cust', 0) or 0))), 
        axis=1
    )
    
    # Enhanced priority - categorize ALL breaks, not just filtering
    def calculate_priority(row):
        cash_impact = row['cash_impact']
        break_type = row.get('break_label', '')
        
        # FX and tax breaks are higher priority due to systemic risk
        if 'fx' in break_type.lower() or 'tax' in break_type.lower():
            if cash_impact > 50000:
                return 'CRITICAL'
            elif cash_impact > 5000:
                return 'HIGH'
        
        # Standard cash impact based priority
        if cash_impact > 100000:
            return 'CRITICAL'
        elif cash_impact > 10000:
            return 'HIGH' 
        elif cash_impact > 1000:
            return 'MEDIUM'
        else:
            return 'LOW'
    
    breaks['priority'] = breaks.apply(calculate_priority, axis=1)
    
    return breaks

if __name__ == "__main__":
    # Fix paths based on your project structure
    project_root = Path(__file__).resolve().parent.parent  # Goes from src/ to NBIM/
    data_dir = project_root / "data"
    out_dir = Path(__file__).resolve().parent / "out"  # src/out/
    
    # Create output directory if it doesn't exist
    out_dir.mkdir(exist_ok=True)
    
    print(f"Looking for data in: {data_dir}")
    print(f"Output directory: {out_dir}")
    
    # Check if files exist
    nbim_file = data_dir / "NBIM_Dividend_Bookings 1 (2).csv"
    custody_file = data_dir / "CUSTODY_Dividend_Bookings 1 (2).csv"
    
    if not nbim_file.exists():
        print(f"❌ Missing file: {nbim_file}")
        exit(1)
    if not custody_file.exists():
        print(f"❌ Missing file: {custody_file}")
        exit(1)
        
    print("✓ Data files found")
    
    # 1. Load and compute everything deterministically
    merged = load_and_align(
        str(nbim_file),
        str(custody_file)
    )
    
    # 2. All deterministic analysis first
    breaks = compute_deterministic_analysis(merged)
    broken = breaks[breaks["break_label"] != "ok"].copy()
    
    if not broken.empty:
        print(f"Found {len(broken)} total breaks")
        
        # NO FILTERING - process ALL breaks, but prioritize them
        material_breaks = broken.copy()  # Now includes all breaks
        
        print(f"Processing ALL {len(material_breaks)} breaks by priority...")
        
        # 3. LLM CALL #1: Smart FX analysis only for FX breaks
        print("Applying FX intelligence to breaks...")
        broken_with_fx = verify_fx_with_intelligence(material_breaks)
        
        # 4. LLM CALL #2: Business synthesis of ALL breaks
        print("Generating comprehensive business summary...")
        final_summary = generate_business_summary(broken_with_fx)
        
        # Save results
        broken_with_fx.to_csv(out_dir / "recon_breaks_detailed.csv", index=False)
        with open(out_dir / "business_summary.md", "w", encoding='utf-8') as f:
            f.write(final_summary)
        
        print("✓ Comprehensive break analysis complete")
        print("✓ FX intelligence applied") 
        print("✓ Complete business summary generated")
        
        # Print summary
        print("\n" + "="*50)
        print("COMPREHENSIVE PRIORITY ACTIONS")
        print("="*50)
        print(final_summary)
    else:
        print("No breaks found - all reconciliations clean!")