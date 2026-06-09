library(tidyverse)
library(sf)

# Constants for ROI Analysis
TAX_RATE <- 0.0125 # 1.25% average property tax rate proxy
MAINT_COST_PER_LANE_MILE <- 10000 # Annual maintenance liability proxy ($10k/mi)

# 1. Load Data
message("Loading datasets...")
census <- read_csv("Transportation_ROI_Analysis/data/oki_census_data.csv", show_col_types = FALSE) %>%
  mutate(GEOID = str_pad(as.character(GEOID), 12, pad = "0"))

awards <- read_csv("Transportation_ROI_Analysis/data/award_tract_mapping.csv", show_col_types = FALSE) %>%
  mutate(GEOID = str_pad(as.character(GEOID), 12, pad = "0")) %>%
  group_by(GEOID) %>%
  summarise(Fed_Investment = sum(assigned_amount), .groups = "drop")

mileage <- read_csv("Transportation_ROI_Analysis/data/oki_tract_mileage.csv", show_col_types = FALSE) %>%
  mutate(GEOID = str_pad(as.character(GEOID), 12, pad = "0"),
         Road_Miles = Road_Meters / 1609.34)

tracts_geo <- st_read("Transportation_ROI_Analysis/data/oki_tracts.geojson", quiet = TRUE) %>%
  mutate(GEOID = str_pad(as.character(GEOID), 12, pad = "0")) %>%
  st_transform(26916)

tracts_geo$Acres <- as.numeric(st_area(tracts_geo)) / 4046.86

# 2. Join & Calculate Metrics
message("Analyzing ROI...")
df <- tracts_geo %>%
  st_drop_geometry() %>%
  left_join(census, by = "GEOID") %>%
  left_join(awards, by = "GEOID") %>%
  left_join(mileage, by = "GEOID") %>%
  mutate(
    Fed_Investment = replace_na(Fed_Investment, 0),
    Road_Miles = replace_na(Road_Miles, 0),
    # Estimate total taxable value (Housing Units * Median Value)
    Total_Housing_Value = Housing_Units * Median_Home_Value,
    # Annual Revenue Estimate
    Est_Annual_Tax_Revenue = Total_Housing_Value * TAX_RATE,
    # Annual Maintenance Liability
    Est_Annual_Maint_Liability = Road_Miles * MAINT_COST_PER_LANE_MILE,
    # ROI Metrics
    Revenue_Per_Acre = Est_Annual_Tax_Revenue / Acres,
    Net_Fiscal_Impact = Est_Annual_Tax_Revenue - Est_Annual_Maint_Liability,
    Fed_Investment_Per_Acre = Fed_Investment / Acres,
    Pop_Density = Population / Acres
  )

# 3. Categorize by Density
df <- df %>%
  mutate(
    Density_Class = case_when(
      Pop_Density >= 10 ~ "Urban",
      Pop_Density >= 2 ~ "Suburban",
      TRUE ~ "Sprawl/Rural"
    )
  )

# 4. Summary Table
summary_roi <- df %>%
  group_by(Density_Class) %>%
  summarise(
    Tract_Count = n(),
    Avg_Revenue_Per_Acre = mean(Revenue_Per_Acre, na.rm=TRUE),
    Avg_Fed_Invest_Per_Acre = mean(Fed_Investment_Per_Acre, na.rm=TRUE),
    Avg_Maint_Liability_Per_Acre = mean(Est_Annual_Maint_Liability / Acres, na.rm=TRUE),
    Net_Fiscal_Impact_Per_Acre = mean(Net_Fiscal_Impact / Acres, na.rm=TRUE),
    .groups = "drop"
  )

print(summary_roi)

# 5. Save Results
write_csv(df, "Transportation_ROI_Analysis/data/oki_roi_results.csv")
write_csv(summary_roi, "Transportation_ROI_Analysis/data/oki_roi_summary.csv")
message("ROI Analysis complete.")
