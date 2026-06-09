import pandas as pd
import re

def extract_info(description):
    description = str(description).upper()
    
    project_type = "Unknown"
    primary_route = ""
    location_detail = ""
    confidence = "Low"
    
    # Identify Project Type
    if any(kw in description for kw in ["BRIDGE", "VIADUCT", "CULVERT"]):
        project_type = "Bridge"
    elif any(kw in description for kw in ["TRAIL", "PEDESTRIAN", "BICYCLE", "BIKE", "SIDEWALK"]) and "TRAIN" not in description:
        # Avoid matching TRAIN as TRAIL if TRAIL isn't explicitly there
        if "TRAIL" in description or any(kw in description for kw in ["PEDESTRIAN", "BICYCLE", "BIKE", "SIDEWALK"]):
             project_type = "Trail"
        else:
             project_type = "Transit"
    elif any(kw in description for kw in ["TRANSIT", "BUS", "SORTA", "TANK", "RAILROAD", "RAIL", "STREETCAR", "TRAIN"]):
        project_type = "Transit"
    elif any(kw in description for kw in ["AIRPORT", "CVG", "LUKEN"]):
        project_type = "Airport"
    elif any(kw in description for kw in ["SAFETY", "SS4A", "SAFE STREETS"]):
        project_type = "Safety"
    elif any(kw in description for kw in ["PLANNING", "DESIGN", "FEASIBILITY", "STUDY"]):
        project_type = "Planning"
    elif any(kw in description for kw in ["ROAD", "HIGHWAY", "INTERSTATE", "STREET", "AVE", "RD", "DR", "WAY"]):
        project_type = "Road"
    elif any(kw in description for kw in ["SIGNAL", "INTERSECTION", "TRAFFIC"]):
        project_type = "Road"

    # Common Route Patterns
    # ODOT style: HAM US 27, HAM IR 75, BUT SR 4, BUT CR 22, HAM-75-3418
    # KY style: KY 8, I-75
    
    # 1. County-based ODOT style: HAM IR 75, BUT SR 129
    counties = ["HAM", "BUT", "CLE", "WAR", "BOO", "KEN", "CAM", "DEA"]
    route_match = re.search(rf'({"|".join(counties)})[- /]*(IR|US|SR|CR|TR|MR|I|OH|KY)[- ]*(\d+[A-Z]?)', description)
    if route_match:
        type_ = route_match.group(2)
        num = route_match.group(3)
        if type_ == "IR": type_ = "I"
        if type_ == "OH": type_ = "SR"
        primary_route = f"{type_}-{num}"
        confidence = "Medium"

    # 2. Standard style: I-75, US 50, SR 125, KY 8
    if not primary_route:
        std_route_match = re.search(r'(I|US|SR|OH|KY|CR|TR|MR)[- ]*(\d+[A-Z]?)', description)
        if std_route_match:
            type_ = std_route_match.group(1)
            num = std_route_match.group(2)
            if type_ == "OH": type_ = "SR"
            primary_route = f"{type_}-{num}"
            confidence = "Medium"
    
    # 3. Direct county-route dash style: HAM-75-3418
    if not primary_route:
        dash_match = re.search(rf'({"|".join(counties)})-(\d+)-(\d+)', description)
        if dash_match:
            primary_route = f"{dash_match.group(1)}-{dash_match.group(2)}"
            confidence = "Medium"
        
    # Western Hills Viaduct special case
    if "WESTERN HILLS VIADUCT" in description or "WHV" in description:
        primary_route = "Western Hills Viaduct"
        confidence = "High"
    
    # Brent Spence Bridge special case
    if "BRENT SPENCE" in description:
        primary_route = "I-71/I-75 (Brent Spence Bridge)"
        confidence = "High"

    # Location Details
    # Between ... and ...
    between_match = re.search(r'BETWEEN\s+(.*?)\s+AND\s+(.*?)(\.|\:|,|;|$)', description)
    if between_match:
        location_detail = f"Between {between_match.group(1).strip()} and {between_match.group(2).strip()}"
        confidence = "High"
    
    # At ...
    at_match = re.search(r'AT\s+(.*?)(\.|\:|,|;|$)', description)
    if at_match and not location_detail:
        location_detail = f"At {at_match.group(1).strip()}"
        confidence = "High"

    # From ... to ...
    from_to_match = re.search(r'FROM\s+(.*?)\s+TO\s+(.*?)(\.|\:|,|;|$)', description)
    if from_to_match and not location_detail:
        location_detail = f"From {from_to_match.group(1).strip()} to {from_to_match.group(2).strip()}"
        confidence = "High"

    # If we found a route but no specific detail, and description is long, maybe we missed something
    if primary_route and confidence == "Medium" and len(description) > 50:
        # Just keep it as medium or try to find intersection
        int_match = re.search(r'INTERSECTION WITH\s+(.*?)(\.|\:|,|;|$)', description)
        if int_match:
            location_detail = f"Intersection with {int_match.group(1).strip()}"
            confidence = "High"

    if description == "AWD MAINTENANCE":
        confidence = "Low"

    return project_type, primary_route, location_detail, confidence

def process_csv(input_path, output_path, limit=250):
    df = pd.read_csv(input_path)
    df_subset = df.head(limit).copy()
    
    results = df_subset['Description'].apply(extract_info)
    df_subset['Project_Type'] = [r[0] for r in results]
    df_subset['Primary_Route'] = [r[1] for r in results]
    df_subset['Location_Detail'] = [r[2] for r in results]
    df_subset['Confidence'] = [r[3] for r in results]
    
    output_df = df_subset[['Award ID', 'Award Amount', 'Description', 'Project_Type', 'Primary_Route', 'Location_Detail', 'Confidence']]
    output_df.to_csv(output_path, index=False)
    print(f"Processed {len(output_df)} rows and saved to {output_path}")

if __name__ == "__main__":
    process_csv('Transportation_ROI_Analysis/data/oki_awards_filtered.csv', 'Transportation_ROI_Analysis/data/oki_awards_with_locations_part1.csv')
