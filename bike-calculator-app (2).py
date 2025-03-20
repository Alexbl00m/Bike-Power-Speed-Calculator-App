import streamlit as st
import pandas as pd
import numpy as np
import math
import plotly.graph_objects as go
from datetime import timedelta

# Set page configuration
st.set_page_config(
    page_title="Bike Power Speed Calculator",
    page_icon="🚴",
    layout="wide"
)

# Apply custom CSS for Montserrat font and branding colors
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Montserrat', sans-serif;
}

.main {
    background-color: #FFFFFF;
}

h1, h2, h3, h4, h5, h6 {
    font-family: 'Montserrat', sans-serif;
    font-weight: 600;
    color: #E6754E;
}

.stButton>button {
    background-color: #E6754E;
    color: white;
    font-family: 'Montserrat', sans-serif;
    border: none;
    border-radius: 4px;
    padding: 8px 16px;
}

.stButton>button:hover {
    background-color: #c45d3a;
}

.highlight {
    color: #E6754E;
    font-weight: 600;
}

.result-box {
    background-color: #f8f8f8;
    padding: 20px;
    border-radius: 10px;
    border-left: 5px solid #E6754E;
}

.output-container {
    background-color: #f8f8f8;
    padding: 15px;
    border-radius: 10px;
    margin-bottom: 20px;
}

.output-label {
    font-weight: 600;
    color: #555;
}

.output-value {
    font-weight: 600;
    color: #333;
    font-size: 18px;
    text-align: right;
}

/* Custom header styling */
.custom-header {
    text-align: center;
    font-size: 36px;
    font-weight: 700;
    color: #2C3E50;
    padding-bottom: 10px;
    border-bottom: 3px solid #E6754E;
    margin-bottom: 30px;
}
</style>
""", unsafe_allow_html=True)

# Constants
AIR_DENSITY_SEA_LEVEL = 1.225  # kg/m³
GRAVITY = 9.8067  # m/s²

# Header
st.markdown("<div class='custom-header'>BIKE POWER SPEED CALCULATOR</div>", unsafe_allow_html=True)

# Create tabs for different calculator modes
tab1, tab2, tab3 = st.tabs(["Power-Speed Calculator", "Training Zones", "Race Predictor"])

# First tab: Power-Speed Calculator
with tab1:
    # Three columns for input form
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### Rider Details")
        
        rider_weight = st.number_input("Rider weight (kg)", min_value=30.0, max_value=150.0, value=75.0, step=0.1)
        bike_weight = st.number_input("Bike weight (kg)", min_value=5.0, max_value=25.0, value=8.0, step=0.1)
        
        # Total system weight
        total_weight = rider_weight + bike_weight
        st.markdown(f"**Total System Weight:** {total_weight:.1f} kg")
        
        # Drivetrain efficiency
        drivetrain_efficiency = st.number_input("Drive train efficiency (%)", min_value=90.0, max_value=100.0, value=97.5, step=0.5)
        
        # FTP
        ftp = st.number_input("Your FTP (watts)", min_value=100, max_value=500, value=250)
    
    with col2:
        st.markdown("### Ride Conditions")
        
        # Terrain
        distance = st.number_input("Distance (km)", min_value=1.0, max_value=300.0, value=40.0, step=5.0)
        total_elevation = st.number_input("Total climb (m)", min_value=0, max_value=5000, value=500, step=50)
        
        # Average grade calculation
        avg_grade = 100 * (total_elevation / (distance * 1000)) if distance > 0 else 0
        st.markdown(f"**Average Grade:** {avg_grade:.2f}%")
        
        # Wind, temperature, altitude
        wind_speed = st.number_input("Wind speed (km/h, + headwind, - tailwind)", min_value=-50.0, max_value=50.0, value=0.0, step=1.0)
        temperature = st.number_input("Temperature (°C)", min_value=-20, max_value=50, value=20)
        altitude = st.number_input("Altitude (m)", min_value=0, max_value=3000, value=100)
        
        # Calculate air density
        air_density = AIR_DENSITY_SEA_LEVEL * math.exp(-altitude/8000) * (273/(273+temperature))
        st.markdown(f"**Air Density:** {air_density:.4f} kg/m³")
    
    with col3:
        st.markdown("### Aerodynamics & Position")
        
        # Position and CdA
        position_options = [
            "Hoods - Relaxed", 
            "Hoods - Regular", 
            "Drops - Regular", 
            "Drops - Tucked", 
            "Aero bars", 
            "TT position"
        ]
        position = st.selectbox("Position", position_options)
        
        # Default CdA values
        default_cda = {
            "Hoods - Relaxed": 0.400,
            "Hoods - Regular": 0.350,
            "Drops - Regular": 0.320,
            "Drops - Tucked": 0.300,
            "Aero bars": 0.270,
            "TT position": 0.230
        }
        
        cda = st.number_input("CdA", min_value=0.15, max_value=0.8, value=default_cda[position], step=0.005)
        
        # Tire selection
        tire_options = [
            "Fast TT tire (0.0025)",
            "Race tire (0.0033)",
            "Training tire (0.0040)",
            "Gravel tire (0.0050)",
            "MTB tire (0.0070)"
        ]
        tire_selection = st.selectbox("Tire type", tire_options)
        
        # Default Crr values
        default_crr = {
            "Fast TT tire (0.0025)": 0.0025,
            "Race tire (0.0033)": 0.0033,
            "Training tire (0.0040)": 0.0040,
            "Gravel tire (0.0050)": 0.0050,
            "MTB tire (0.0070)": 0.0070
        }
        
        crr = st.number_input("Crr", min_value=0.0010, max_value=0.0120, value=default_crr[tire_selection], step=0.0001, format="%.4f")
        
        # Target selection
        target_type = st.radio("Calculation target", ["Power", "Speed"])
        
        if target_type == "Power":
            target_speed = st.number_input("Target speed (km/h)", min_value=10.0, max_value=60.0, value=30.0, step=1.0)
        else:  # Speed
            target_power = st.number_input("Target power (watts)", min_value=50, max_value=500, value=200, step=10)
    
    # Calculations section
    st.markdown("---")
    st.markdown("## Results")
    
    # Convert wind speed to m/s
    wind_speed_ms = wind_speed / 3.6
    
    # Convert target speed to m/s for calculation
    target_speed_ms = target_speed / 3.6 if target_type == "Power" else 0
    
    # Calculate power required or speed achievable
    def calculate_power(speed_ms, total_weight, grade, cda, crr, wind_speed_ms, air_density, drivetrain_efficiency):
        # Speed relative to air (accounting for wind)
        relative_speed_ms = speed_ms + wind_speed_ms
        
        # Rolling resistance force
        f_rolling = total_weight * GRAVITY * crr * math.cos(math.atan(grade/100))
        
        # Grade resistance force
        f_grade = total_weight * GRAVITY * math.sin(math.atan(grade/100))
        
        # Air resistance force
        f_air = 0.5 * cda * air_density * relative_speed_ms**2
        
        # Total resistance force
        f_total = f_rolling + f_grade + f_air
        
        # Power required
        power = f_total * speed_ms / (drivetrain_efficiency / 100)
        
        return power, f_rolling, f_grade, f_air
    
    def calculate_speed(power, total_weight, grade, cda, crr, wind_speed_ms, air_density, drivetrain_efficiency):
        # Adjust power for drivetrain efficiency
        power_at_wheel = power * (drivetrain_efficiency / 100)
        
        # Function to find speed given power
        def power_diff(speed_ms):
            # Calculate power required at given speed
            required_power, _, _, _ = calculate_power(speed_ms, total_weight, grade, cda, crr, wind_speed_ms, air_density, 100)
            return required_power - power_at_wheel
        
        # Binary search to find speed
        speed_min, speed_max = 0.1, 30.0  # m/s
        
        for _ in range(50):  # 50 iterations should be enough for good precision
            speed_mid = (speed_min + speed_max) / 2
            if power_diff(speed_mid) > 0:
                speed_max = speed_mid
            else:
                speed_min = speed_mid
                
        return (speed_min + speed_max) / 2
    
    # Calculate values based on target type
    if target_type == "Power":
        # Calculate power required for given speed
        required_power, f_rolling, f_grade, f_air = calculate_power(target_speed_ms, total_weight, avg_grade, cda, crr, wind_speed_ms, air_density, drivetrain_efficiency)
        speed_kph = target_speed
    else:  # Speed
        # Calculate speed based on given power
        speed_ms = calculate_speed(target_power, total_weight, avg_grade, cda, crr, wind_speed_ms, air_density, drivetrain_efficiency)
        speed_kph = speed_ms * 3.6  # Convert to km/h
        required_power = target_power
        # Calculate forces for power distribution
        _, f_rolling, f_grade, f_air = calculate_power(speed_ms, total_weight, avg_grade, cda, crr, wind_speed_ms, air_density, drivetrain_efficiency)
    
    # Calculate time
    time_hours = distance / speed_kph
    finish_time = str(timedelta(seconds=int(time_hours * 3600)))
    
    # Calculate training metrics
    intensity_factor = required_power / ftp if ftp > 0 else 0
    training_stress_score = (time_hours) * (intensity_factor ** 2) * 100 if ftp > 0 else 0
    
    # Determine workout difficulty
    if intensity_factor < 0.55:
        workout_difficulty = "Recovery"
    elif intensity_factor < 0.75:
        workout_difficulty = "Endurance"
    elif intensity_factor < 0.90:
        workout_difficulty = "Tempo"
    elif intensity_factor < 1.05:
        workout_difficulty = "Threshold"
    elif intensity_factor < 1.20:
        workout_difficulty = "VO2 Max"
    else:
        workout_difficulty = "Anaerobic"
    
    # Results display
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("<div class='output-container'>", unsafe_allow_html=True)
        st.markdown(f"<div class='output-label'>Required Power</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='output-value'>{required_power:.1f} W</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("<div class='output-container'>", unsafe_allow_html=True)
        st.markdown(f"<div class='output-label'>Power to Weight</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='output-value'>{required_power/rider_weight:.2f} W/kg</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col2:
        st.markdown("<div class='output-container'>", unsafe_allow_html=True)
        st.markdown(f"<div class='output-label'>Average Speed</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='output-value'>{speed_kph:.2f} km/h</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("<div class='output-container'>", unsafe_allow_html=True)
        st.markdown(f"<div class='output-label'>Finish Time</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='output-value'>{finish_time}</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col3:
        st.markdown("<div class='output-container'>", unsafe_allow_html=True)
        st.markdown(f"<div class='output-label'>Intensity Factor</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='output-value'>{intensity_factor:.2f} IF</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("<div class='output-container'>", unsafe_allow_html=True)
        st.markdown(f"<div class='output-label'>Training Stress Score</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='output-value'>{training_stress_score:.1f} TSS</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Power distribution
    if 'f_rolling' in locals() and 'f_grade' in locals() and 'f_air' in locals():
        st.markdown("### Power Distribution")
        
        # Calculate power components
        speed_for_calc = target_speed_ms if target_type == "Power" else speed_ms
        p_rolling = f_rolling * speed_for_calc
        p_grade = f_grade * speed_for_calc
        p_air = f_air * speed_for_calc
        p_total = p_rolling + p_grade + p_air
        
        # Calculate percentages
        pct_rolling = p_rolling / p_total * 100
        pct_grade = p_grade / p_total * 100
        pct_air = p_air / p_total * 100
        
        # Display as horizontal bar chart
        fig = go.Figure()
        
        # Add bars
        fig.add_trace(go.Bar(
            y=['Power Distribution'],
            x=[pct_rolling],
            name='Rolling Resistance',
            orientation='h',
            marker=dict(color='#4CAF50')
        ))
        
        fig.add_trace(go.Bar(
            y=['Power Distribution'],
            x=[pct_grade],
            name='Grade Resistance',
            orientation='h',
            marker=dict(color='#FF9800')
        ))
        
        fig.add_trace(go.Bar(
            y=['Power Distribution'],
            x=[pct_air],
            name='Air Resistance',
            orientation='h',
            marker=dict(color='#2196F3')
        ))
        
        # Update layout
        fig.update_layout(
            barmode='stack',
            height=150,
            margin=dict(l=20, r=20, t=20, b=20),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            xaxis=dict(title='Percentage of Total Power')
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Add numeric values
        col1, col2, col3 = st.columns(3)
        col1.metric("Rolling Resistance", f"{p_rolling:.1f} W", f"{pct_rolling:.1f}%")
        col2.metric("Grade Resistance", f"{p_grade:.1f} W", f"{pct_grade:.1f}%")
        col3.metric("Air Resistance", f"{p_air:.1f} W", f"{pct_air:.1f}%")

# Second tab: Training Zones
with tab2:
    st.markdown("### Training Zones Calculator")
    
    # FTP input
    ftp_zones = st.number_input("Enter your FTP (watts)", min_value=100, max_value=500, value=250, key="ftp_zones")
    
    # Calculate zones
    zones = {
        "Zone 1 (Active Recovery)": [0, 0.55*ftp_zones],
        "Zone 2 (Endurance)": [0.56*ftp_zones, 0.75*ftp_zones],
        "Zone 3 (Tempo)": [0.76*ftp_zones, 0.90*ftp_zones],
        "Zone 4 (Threshold)": [0.91*ftp_zones, 1.05*ftp_zones],
        "Zone 5 (VO2 Max)": [1.06*ftp_zones, 1.20*ftp_zones],
        "Zone 6 (Anaerobic Capacity)": [1.21*ftp_zones, 1.50*ftp_zones],
        "Zone 7 (Neuromuscular Power)": [1.51*ftp_zones, 2.50*ftp_zones]
    }
    
    # Create dataframe for display
    zones_df = pd.DataFrame({
        "Zone": list(zones.keys()),
        "Lower Bound (watts)": [int(zone[0]) for zone in zones.values()],
        "Upper Bound (watts)": [int(zone[1]) for zone in zones.values()],
        "Training Focus": [
            "Very easy, recovery", 
            "Long endurance rides, fat metabolism", 
            "Sustained efforts, improved efficiency", 
            "Improve lactate threshold", 
            "Improve VO2 Max, oxygen utilization", 
            "Develop anaerobic capacity, tolerate lactate", 
            "Develop neuromuscular power, sprinting"
        ]
    })
    
    # Display the zones table
    st.table(zones_df)
    
    # Visualization of zones
    st.markdown("### Power Zones Visualization")
    
    fig = go.Figure()
    
    # Define zone colors
    zone_colors = ['#ccfdcc', '#94d494', '#4eb74e', '#ffd700', '#ffaa00', '#ff5555', '#ff0000']
    
    # Create bar chart
    for i, (zone_name, (lower, upper)) in enumerate(zones.items()):
        fig.add_trace(go.Bar(
            x=[zone_name.split(" ")[0]], 
            y=[upper - lower],
            base=[lower],
            marker_color=zone_colors[i],
            name=zone_name,
            text=[f"{int(lower)}-{int(upper)}W"],
            textposition="inside",
            insidetextanchor="middle"
        ))
    
    fig.update_layout(
        title="FTP Power Zones",
        xaxis_title="Power Zones",
        yaxis_title="Power (watts)",
        barmode='stack',
        height=500
    )
    
    st.plotly_chart(fig, use_container_width=True)

# Third tab: Race Predictor
with tab3:
    st.markdown("### Race Predictor")
    
    # Simple layout with basic inputs
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Rider Details")
        
        ftp_race = st.number_input("Your FTP (watts)", min_value=100, max_value=500, value=250, key="ftp_race")
        weight_race = st.number_input("Your weight (kg)", min_value=40.0, max_value=150.0, value=75.0, step=0.5, key="weight_race")
        
        # Calculate power-to-weight
        power_to_weight = ftp_race / weight_race
        st.markdown(f"**Power-to-weight ratio: {power_to_weight:.2f} W/kg**")
        
        # Event details
        st.markdown("#### Event Details")
        
        event_type = st.selectbox("Event type", ["Time trial", "Road race", "Criterium", "Gran fondo"])
        event_distance = st.number_input("Distance (km)", min_value=5.0, max_value=300.0, value=40.0, step=5.0, key="race_distance")
        
    with col2:
        st.markdown("#### Predictions")
        
        # Basic power estimation (simplified calculation)
        if event_type == "Time trial":
            power_percent = 0.95
        elif event_type == "Road race":
            power_percent = 0.85
        elif event_type == "Criterium":
            power_percent = 0.90
        else:  # Gran fondo
            power_percent = 0.80
            
        sustainable_power = ftp_race * power_percent
        
        # Basic speed estimation
        estimated_speed = 25 + (power_to_weight - 3) * 5  # Simple formula
        
        # Time calculation
        time_hours = event_distance / estimated_speed
        hours = int(time_hours)
        minutes = int((time_hours - hours) * 60)
        seconds = int(((time_hours - hours) * 60 - minutes) * 60)
        
        # Display results in simple format
        st.markdown(f"**Sustainable power:** {sustainable_power:.0f} watts ({power_percent*100:.0f}% of FTP)")
        st.markdown(f"**Estimated average speed:** {estimated_speed:.1f} km/h")
        st.markdown(f"**Estimated finish time:** {hours:02d}:{minutes:02d}:{seconds:02d}")
        
        # Simple pacing advice
        st.markdown("#### Pacing Advice")
        st.markdown(f"- **Start:** {sustainable_power * 1.05:.0f} watts (first few minutes)")
        st.markdown(f"- **Middle:** {sustainable_power:.0f} watts (maintain steady effort)")
        st.markdown(f"- **Finish:** {sustainable_power * 1.03:.0f} watts (if you feel strong)")
    
    # Classification table
    st.markdown("---")
    st.markdown("### Rider Classification")
    
    # Create classification table
    classifications = {
        "Category": ["Professional", "Cat 1/Elite", "Cat 2", "Cat 3", "Cat 4/5", "Beginner"],
        "FTP (W/kg)": ["5.0+", "4.0-5.0", "3.5-4.0", "3.0-3.5", "2.5-3.0", "< 2.5"],
        "Description": [
            "World Tour/Professional Continental level",
            "Elite amateur, potential professional",
            "Strong amateur racer, regional competitive",
            "Intermediate club racer",
            "Recreational racer, beginning competitive cyclist",
            "New to cycling or casual rider"
        ]
    }
    
    class_df = pd.DataFrame(classifications)
    st.table(class_df)
    
    # Show user's classification
    if power_to_weight >= 5.0:
        user_category = "Professional"
    elif power_to_weight >= 4.0:
        user_category = "Cat 1/Elite"
    elif power_to_weight >= 3.5:
        user_category = "Cat 2"
    elif power_to_weight >= 3.0:
        user_category = "Cat 3"
    elif power_to_weight >= 2.5:
        user_category = "Cat 4/5"
    else:
        user_category = "Beginner"
        
    st.markdown(f"**Your rider category based on power-to-weight ratio: {user_category}**")