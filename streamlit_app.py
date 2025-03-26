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

footer {
    font-family: 'Montserrat', sans-serif;
    font-size: 12px;
    color: #888888;
    text-align: center;
    margin-top: 50px;
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

/* Styling for result cards */
.metric-card {
    background-color: #f8f8f8;
    border-radius: 10px;
    padding: 15px;
    box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    margin-bottom: 10px;
}
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("<div class='custom-header'>BIKE POWER SPEED CALCULATOR</div>", unsafe_allow_html=True)

# Create tabs for different calculator modes
tab1, tab2, tab3 = st.tabs(["Power-Speed Calculator", "Training Metrics", "Race Predictor"])

# Constants
AIR_DENSITY_SEA_LEVEL = 1.225  # kg/m³
GRAVITY = 9.8067  # m/s²

with tab1:
    # Create three columns for input form
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### Rider Details")
        
        # Unit system selection
        unit_choice = st.selectbox("Unit choice", ["Metric", "Imperial"])
        
        # Weight inputs
        if unit_choice == "Metric":
            rider_weight = st.number_input("Rider weight", min_value=30.0, max_value=150.0, value=75.0, step=0.1, help="Weight in kg")
            clothes_gear_weight = st.number_input("Clothes & gear", min_value=0.0, max_value=20.0, value=1.5, step=0.1, help="Weight in kg")
            bike_weight = st.number_input("Bike weight", min_value=5.0, max_value=25.0, value=8.0, step=0.1, help="Weight in kg")
            weight_unit = "kg"
        else:
            rider_weight_lbs = st.number_input("Rider weight", min_value=66.0, max_value=330.0, value=165.0, step=0.1, help="Weight in lbs")
            clothes_gear_weight_lbs = st.number_input("Clothes & gear", min_value=0.0, max_value=44.0, value=3.3, step=0.1, help="Weight in lbs")
            bike_weight_lbs = st.number_input("Bike weight", min_value=11.0, max_value=55.0, value=17.6, step=0.1, help="Weight in lbs")
            
            # Convert to metric for calculations
            rider_weight = rider_weight_lbs / 2.20462
            clothes_gear_weight = clothes_gear_weight_lbs / 2.20462
            bike_weight = bike_weight_lbs / 2.20462
            weight_unit = "lbs"
        
        # Drivetrain efficiency
        drivetrain_efficiency = st.number_input("Drive train efficiency (%)", min_value=90.0, max_value=100.0, value=97.5, step=0.5, help="Typically 95-98% for clean chains")
        
        # Known FTP/CP
        ftp = st.number_input("Known FTP/CP", min_value=100, max_value=500, value=250, help="Functional Threshold Power in watts")
        
        # Calculate total system weight
        total_weight = rider_weight + clothes_gear_weight + bike_weight
        
        st.markdown(f"**Total System Weight:** {total_weight:.1f} {weight_unit}")
    
    with col2:
        st.markdown("### Ride Conditions")
        
        # Terrain and environment
        if unit_choice == "Metric":
            distance = st.number_input("Distance", min_value=1.0, max_value=300.0, value=40.0, step=5.0, help="Distance in km")
            total_elevation = st.number_input("Total climb", min_value=0, max_value=5000, value=500, step=50, help="Total elevation gain in meters")
            distance_unit = "km"
            elevation_unit = "m"
        else:
            distance_miles = st.number_input("Distance", min_value=1.0, max_value=186.0, value=25.0, step=5.0, help="Distance in miles")
            total_elevation_feet = st.number_input("Total climb", min_value=0, max_value=16000, value=1640, step=100, help="Total elevation gain in feet")
            
            # Convert to metric for calculations
            distance = distance_miles * 1.60934
            total_elevation = total_elevation_feet * 0.3048
            distance_unit = "miles"
            elevation_unit = "ft"
        
        # Average grade calculation
        avg_grade = 100 * (total_elevation / (distance * 1000)) if distance > 0 else 0
        st.markdown(f"**Average Grade:** {avg_grade:.2f}%")
        
        # Wind speed
        if unit_choice == "Metric":
            wind_speed = st.number_input("Wind (+ headwind, - tailwind)", min_value=-50.0, max_value=50.0, value=0.0, step=1.0, help="Wind speed in km/h")
            wind_unit = "km/h"
        else:
            wind_speed_mph = st.number_input("Wind (+ headwind, - tailwind)", min_value=-30.0, max_value=30.0, value=0.0, step=1.0, help="Wind speed in mph")
            wind_speed = wind_speed_mph * 1.60934
            wind_unit = "mph"
        
        # Temperature, altitude and air density
        temperature = st.number_input("Temperature", min_value=-20, max_value=50, value=20, help="Temperature in °C")
        altitude = st.number_input("Altitude", min_value=0, max_value=3000, value=100, help="Altitude in meters")
        
        # Calculate air density based on temperature and altitude
        # Simple model: air_density = AIR_DENSITY_SEA_LEVEL * exp(-altitude/8000) * (273/(273+temperature))
        air_density = AIR_DENSITY_SEA_LEVEL * math.exp(-altitude/8000) * (273/(273+temperature))
        st.markdown(f"**Air Density:** {air_density:.4f} kg/m³")
        
    with col3:
        st.markdown("### Aerodynamics & Position")
        
        # Position selection and CdA
        position_options = [
            "Hoods - Relaxed",
            "Hoods - Regular",
            "Drops - Regular",
            "Drops - Tucked",
            "Aero bars",
            "TT position"
        ]
        position = st.selectbox("Position", position_options)
        
        # Default CdA values based on position
        default_cda = {
            "Hoods - Relaxed": 0.400,
            "Hoods - Regular": 0.350,
            "Drops - Regular": 0.320,
            "Drops - Tucked": 0.300,
            "Aero bars": 0.270,
            "TT position": 0.230
        }
        
        cda = st.number_input("CdA override", min_value=0.15, max_value=0.8, value=default_cda[position], step=0.005, help="Drag coefficient * frontal area")
        
        # Rolling resistance and tire selection
        tire_options = [
            "Fast TT tire (0.0025)",
            "Race tire (0.0033)",
            "Training tire (0.0040)",
            "Gravel tire (0.0050)",
            "MTB tire (0.0070)"
        ]
        tire_selection = st.selectbox("Tire type", tire_options)
        
        # Default Crr values based on tire type
        default_crr = {
            "Fast TT tire (0.0025)": 0.0025,
            "Race tire (0.0033)": 0.0033,
            "Training tire (0.0040)": 0.0040,
            "Gravel tire (0.0050)": 0.0050,
            "MTB tire (0.0070)": 0.0070
        }
        
        crr = st.number_input("Crr override", min_value=0.0010, max_value=0.0120, value=default_crr[tire_selection], 
                              step=0.0001, format="%.4f", help="Coefficient of rolling resistance")
        
        # Finish time input (optional)
        st.markdown("### Target")
        
        target_type = st.radio("Target type", ["Power", "Speed", "Time"])
        
        if target_type == "Time":
            col1, col2, col3 = st.columns(3)
            with col1:
                hours = st.number_input("Hours", min_value=0, max_value=24, value=1, step=1)
            with col2:
                minutes = st.number_input("Minutes", min_value=0, max_value=59, value=30, step=1)
            with col3:
                seconds = st.number_input("Seconds", min_value=0, max_value=59, value=0, step=1)
            
            total_seconds = hours * 3600 + minutes * 60 + seconds
            target_speed = distance * 3600 / total_seconds if total_seconds > 0 else 0
            
        elif target_type == "Speed":
            if unit_choice == "Metric":
                target_speed = st.number_input("Target speed", min_value=10.0, max_value=60.0, value=30.0, step=1.0, help="Speed in km/h")
            else:
                target_speed_mph = st.number_input("Target speed", min_value=6.0, max_value=40.0, value=18.0, step=1.0, help="Speed in mph")
                target_speed = target_speed_mph * 1.60934
            
            total_seconds = distance * 3600 / target_speed if target_speed > 0 else 0
            
        else:  # Power
            target_power = st.number_input("Target power", min_value=50, max_value=500, value=200, step=10, help="Power in watts")
            
            # Calculate target speed based on power (we'll define this calculation below)
            # For now, just a placeholder
            target_speed = 0  # Will be calculated
            total_seconds = 0  # Will be calculated
    
    # Calculations section
    st.markdown("---")
    st.markdown("## Results")
    
    # Convert wind speed to m/s
    wind_speed_ms = wind_speed / 3.6
    
    # Convert target speed to m/s for calculation
    target_speed_ms = target_speed / 3.6
    
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
            required_power, _, _, _ = calculate_power(speed_ms, total_weight, grade, cda, crr, wind_speed_ms, air_density, 100)  # Efficiency already applied
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
        # Calculate speed based on given power
        speed_ms = calculate_speed(target_power, total_weight, avg_grade, cda, crr, wind_speed_ms, air_density, drivetrain_efficiency)
        target_speed = speed_ms * 3.6  # Convert to km/h
        total_seconds = distance * 3600 / target_speed if target_speed > 0 else 0
        required_power = target_power
        
    else:  # Target is either Time or Speed
        # Calculate power required for given speed
        required_power, f_rolling, f_grade, f_air = calculate_power(target_speed_ms, total_weight, avg_grade, cda, crr, wind_speed_ms, air_density, drivetrain_efficiency)
    
    # Calculate derived metrics
    intensity_factor = required_power / ftp if ftp > 0 else 0
    normalized_power = required_power  # Simplified for steady state
    training_stress_score = (total_seconds / 3600) * (normalized_power / ftp) ** 2 * 100 if ftp > 0 else 0
    
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
    
    # Format finish time
    finish_time = str(timedelta(seconds=int(total_seconds)))
    
    # Results section with three columns
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
        
        st.markdown("<div class='output-container'>", unsafe_allow_html=True)
        st.markdown(f"<div class='output-label'>Intensity Factor</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='output-value'>{intensity_factor:.2f} IF</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col2:
        st.markdown("<div class='output-container'>", unsafe_allow_html=True)
        st.markdown(f"<div class='output-label'>Average Speed</div>", unsafe_allow_html=True)
        if unit_choice == "Metric":
            st.markdown(f"<div class='output-value'>{target_speed:.2f} km/h</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='output-value'>{target_speed/1.60934:.2f} mph</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("<div class='output-container'>", unsafe_allow_html=True)
        st.markdown(f"<div class='output-label'>Finish Time</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='output-value'>{finish_time}</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("<div class='output-container'>", unsafe_allow_html=True)
        st.markdown(f"<div class='output-label'>Training Stress Score</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='output-value'>{training_stress_score:.1f} TSS</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col3:
        st.markdown("<div class='output-container'>", unsafe_allow_html=True)
        st.markdown(f"<div class='output-label'>Workout Classification</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='output-value'>{workout_difficulty}</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
        if 'f_rolling' in locals() and 'f_grade' in locals() and 'f_air' in locals():
            # Create power distribution chart
            labels = ['Rolling Resistance', 'Grade Resistance', 'Air Resistance']
            values = [f_rolling * target_speed_ms, f_grade * target_speed_ms, f_air * target_speed_ms]
            
            # Calculate percentages
            total = sum(values)
            percentages = [v/total*100 for v in values]
            
            # Show power distribution
            st.markdown("<div class='output-label' style='margin-bottom: 10px;'>Power Distribution</div>", unsafe_allow_html=True)
            
            # Simplified bar chart with colored boxes
            cols = st.columns(3)
            colors = ['#4CAF50', '#FF9800', '#2196F3']
            
            for i, (col, label, percentage, color) in enumerate(zip(cols, labels, percentages, colors)):
                col.markdown(f"""
                <div style="background-color: {color}; color: white; padding: 10px; border-radius: 5px; text-align: center;">
                    <div style="font-size: 14px;">{label}</div>
                    <div style="font-size: 18px; font-weight: bold;">{percentage:.1f}%</div>
                </div>
                """, unsafe_allow_html=True)
    
    # Add visualization section
    st.markdown("---")
    
    # Basic speed chart
    speeds = np.linspace(10, 45, 36)  # speeds from 10 to 45 km/h
    speeds_ms = speeds / 3.6  # convert to m/s
    
    powers = []
    for speed_ms in speeds_ms:
        power, _, _, _ = calculate_power(speed_ms, total_weight, avg_grade, cda, crr, wind_speed_ms, air_density, drivetrain_efficiency)
        powers.append(power)
    
    # Create speed-power curve
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=speeds,
        y=powers,
        mode='lines',
        name='Power Required',
        line=dict(color='#E6754E', width=2)
    ))
    
    # Add marker for current calculation
    fig.add_trace(go.Scatter(
        x=[target_speed],
        y=[required_power],
        mode='markers',
        name='Current Point',
        marker=dict(color='#2C3E50', size=10)
    ))
    
    # Add FTP line
    fig.add_shape(
        type="line",
        x0=min(speeds),
        y0=ftp,
        x1=max(speeds),
        y1=ftp,
        line=dict(
            color="Red",
            width=2,
            dash="dash",
        )
    )
    
    fig.add_annotation(
        x=min(speeds),
        y=ftp,
        text="FTP",
        showarrow=False,
        yshift=10,
        font=dict(color="Red")
    )
    
    fig.update_layout(
        title="Speed vs Power",
        xaxis_title="Speed (km/h)",
        yaxis_title="Power (Watts)",
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01
        ),
        margin=dict(l=20, r=20, t=40, b=20),
    )
    
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.markdown("### Training Metrics Calculator")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Input")
        
        ftp_training = st.number_input("Your FTP (watts)", min_value=100, max_value=500, value=250, help="Functional Threshold Power", key="ftp_training")
        
        workout_type = st.radio("Workout type", ["Actual (with data)", "Planned"])
        
        if workout_type == "Actual (with data)":
            avg_power = st.number_input("Average Power (watts)", min_value=50, max_value=500, value=200)
            normalized_power = st.number_input("Normalized Power (watts)", min_value=50, max_value=500, value=210)
            duration_hours = st.number_input("Duration (hours)", min_value=0.0, max_value=24.0, value=1.5, step=0.25)
            
            # Calculate metrics
            intensity = normalized_power / ftp_training if ftp_training > 0 else 0
            tss = (duration_hours * 3600) * normalized_power * intensity / (ftp_training * 3600) * 100 if ftp_training > 0 else 0
            
        else:  # Planned workout
            workout_intensity = st.slider("Planned intensity (% of FTP)", min_value=40, max_value=150, value=75, step=5)
            duration_hours = st.number_input("Planned duration (hours)", min_value=0.25, max_value=10.0, value=1.5, step=0.25)
            
            # Convert to decimal
            intensity = workout_intensity / 100
            
            # For planned workout, average power = normalized power = intensity * FTP
            avg_power = intensity * ftp_training
            normalized_power = avg_power
            
            # Calculate TSS
            tss = (duration_hours * 3600) * normalized_power * intensity / (ftp_training * 3600) * 100 if ftp_training > 0 else 0
    
    with col2:
        st.markdown("#### Results")
        
        # Determine training zone
        if intensity <= 0.55:
            zone = "Zone 1 - Active Recovery"
            zone_description = "Very easy, recovery ride"
        elif intensity <= 0.75:
            zone = "Zone 2 - Endurance"
            zone_description = "Long, sustained efforts to build aerobic endurance"
        elif intensity <= 0.90:
            zone = "Zone 3 - Tempo"
            zone_description = "Moderate intensity, 'comfortably hard' effort"
        elif intensity <= 1.05:
            zone = "Zone 4 - Threshold"
            zone_description = "Lactate threshold training, challenging but sustainable"
        elif intensity <= 1.20:
            zone = "Zone 5 - VO2 Max"
            zone_description = "High intensity, improves maximal oxygen uptake"
        else:
            zone = "Zone 6 - Anaerobic"
            zone_description = "Very high intensity, improves anaerobic capacity"
        
        # Classify workout difficulty based on TSS
        if tss < 100:
            difficulty = "Low"
            recovery_time = "12-24 hours"
        elif tss < 200:
            difficulty = "Medium"
            recovery_time = "24-36 hours"
        elif tss < 300:
            difficulty = "High"
            recovery_time = "36-48 hours"
        elif tss < 400:
            difficulty = "Very High"
            recovery_time = "48-72 hours"
        else:
            difficulty = "Extreme"
            recovery_time = "72+ hours"
        
        # Display results in a nice format
        st.markdown(f"""
        <div class="metric-card">
            <h4 style="color:#E6754E;">Training Intensity</h4>
            <div style="font-size: 28px; font-weight: bold;">{intensity:.2f} IF</div>
            <p>{zone}</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="metric-card">
            <h4 style="color:#E6754E;">Training Stress Score</h4>
            <div style="font-size: 28px; font-weight: bold;">{tss:.1f} TSS</div>
            <p>Difficulty: {difficulty}</p>
            <p>Recommended recovery: {recovery_time}</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="metric-card">
            <h4 style="color:#E6754E;">Power Metrics</h4>
            <p><strong>Average Power:</strong> {avg_power:.1f} W ({avg_power/ftp_training*100:.1f}% of FTP)</p>
            <p><strong>Normalized Power:</strong> {normalized_power:.1f} W ({normalized_power/ftp_training*100:.1f}% of FTP)</p>
            <p><strong>Duration:</strong> {duration_hours:.2f} hours ({int(duration_hours * 60)} minutes)</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Training zones reference
    st.markdown("---")
    st.markdown("### Training Zones Reference")
    
    # Create a table of training zones
    zones_data = {
        "Zone": ["Zone 1", "Zone 2", "Zone 3", "Zone 4", "Zone 5", "Zone 6", "Zone 7"],
        "Name": ["Active Recovery", "Endurance", "Tempo", "Threshold", "VO2 Max", "Anaerobic", "Neuromuscular"],
        "% of FTP": ["< 55%", "55-75%", "76-90%", "91-105%", "106-120%", "121-150%", "> 150%"],
        "Description": [
            "Very easy, recovery",
            "Long endurance rides, fat metabolism",
            "Sustained efforts, improved efficiency",
            "Improve lactate threshold",
            "Improve VO2 Max, oxygen utilization",
            "Develop anaerobic capacity, tolerate lactate",
            "Develop neuromuscular power, sprinting"
        ],
        "Typical Duration": [
            "60-90+ min",
            "2-6 hours",
            "30-90 min",
            "20-60 min",
            "3-12 min",
            "30 sec-3 min",
            "5-30 sec"
        ]
    }
    
    # Convert to DataFrame and display
    zones_df = pd.DataFrame(zones_data)
    st.table(zones_df)
    
    # Add power-based training zones calculation
    if ftp_training > 0:
        st.markdown("### Your Power Zones")
        
        # Calculate personalized power zones based on FTP
        personal_zones = {
            "Zone": ["Zone 1", "Zone 2", "Zone 3", "Zone 4", "Zone 5", "Zone 6", "Zone 7"],
            "Name": ["Active Recovery", "Endurance", "Tempo", "Threshold", "VO2 Max", "Anaerobic", "Neuromuscular"],
            "Power Range (watts)": [
                f"< {int(0.55 * ftp_training)}",
                f"{int(0.55 * ftp_training)} - {int(0.75 * ftp_training)}",
                f"{int(0.76 * ftp_training)} - {int(0.90 * ftp_training)}",
                f"{int(0.91 * ftp_training)} - {int(1.05 * ftp_training)}",
                f"{int(1.06 * ftp_training)} - {int(1.20 * ftp_training)}",
                f"{int(1.21 * ftp_training)} - {int(1.50 * ftp_training)}",
                f"> {int(1.50 * ftp_training)}"
            ]
        }
        
        # Convert to DataFrame and display
        personal_zones_df = pd.DataFrame(personal_zones)
        st.table(personal_zones_df)
    
    # Show a visualization of the training zones
    fig = go.Figure()
    
    # Define zone boundary percentages
    zone_boundaries = [0, 0.55, 0.75, 0.90, 1.05, 1.20, 1.50, 2.0]
    zone_colors = ['#ccfdcc', '#94d494', '#4eb74e', '#ffd700', '#ffaa00', '#ff5555', '#ff0000']
    zone_names = ['Z1', 'Z2', 'Z3', 'Z4', 'Z5', 'Z6', 'Z7']
    
    # Power range for x-axis
    power_range = np.linspace(0, ftp_training * 2, 100)
    
    # Add vertical lines for zone boundaries
    for i, boundary in enumerate(zone_boundaries[1:-1], 1):
        fig.add_shape(
            type="line",
            x0=boundary * ftp_training,
            y0=0,
            x1=boundary * ftp_training,
            y1=1,
            line=dict(
                color="gray",
                width=1,
                dash="dash",
            )
        )
    
    # Add colored rectangles for each zone
    for i in range(len(zone_names)):
        fig.add_shape(
            type="rect",
            x0=zone_boundaries[i] * ftp_training,
            x1=zone_boundaries[i+1] * ftp_training,
            y0=0,
            y1=1,
            fillcolor=zone_colors[i],
            opacity=0.5,
            line=dict(width=0),
        )
        
        # Add zone labels
        fig.add_annotation(
            x=((zone_boundaries[i] + zone_boundaries[i+1]) / 2) * ftp_training,
            y=0.5,
            text=zone_names[i],
            showarrow=False,
            font=dict(size=12, color="black")
        )
    
    fig.update_layout(
        title="Power Zones Based on Your FTP",
        xaxis_title="Power (Watts)",
        yaxis=dict(
            showticklabels=False,
            showgrid=False,
            zeroline=False,
        ),
        height=200,
        margin=dict(l=20, r=20, t=40, b=20),
        showlegend=False
    )
    
    st.plotly_chart(fig, use_container_width=True)

# Replace the Race Predictor tab section with this updated code

with tab3:
    st.markdown("### Race Predictor")
    
    # Simple layout with basic inputs
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Rider Details")
        
        ftp_race = st.number_input("Your FTP (watts)", min_value=100, max_value=500, value=250, key="ftp_race")
        weight_race = st.number_input("Your weight (kg)", min_value=40.0, max_value=150.0, value=75.0, step=0.5, key="weight_race")
        
        # Additional inputs needed for proper calculation
        clothes_gear_weight_race = st.number_input("Clothes & gear (kg)", min_value=0.0, max_value=20.0, value=1.5, step=0.1, key="clothes_gear_race")
        bike_weight_race = st.number_input("Bike weight (kg)", min_value=5.0, max_value=25.0, value=8.0, step=0.1, key="bike_weight_race")
        
        # Calculate total system weight
        total_weight_race = weight_race + clothes_gear_weight_race + bike_weight_race
        
        # Calculate power-to-weight
        power_to_weight = ftp_race / weight_race
        st.markdown(f"**Power-to-weight ratio: {power_to_weight:.2f} W/kg**")
        st.markdown(f"**Total system weight: {total_weight_race:.1f} kg**")
        
        # Event details
        st.markdown("#### Event Details")
        
        event_type = st.selectbox("Event type", ["Time trial", "Road race", "Criterium", "Gran fondo"])
        event_distance = st.number_input("Distance (km)", min_value=5.0, max_value=300.0, value=40.0, step=5.0, key="race_distance")
        
        # Add additional ride conditions for proper physics calculation
        st.markdown("#### Ride Conditions")
        
        total_elevation = st.number_input("Total climb (m)", min_value=0, max_value=5000, value=100, step=50, key="race_elevation")
        wind_speed = st.number_input("Wind (+ headwind, - tailwind) (km/h)", min_value=-50.0, max_value=50.0, value=0.0, step=1.0, key="race_wind")
        temperature = st.number_input("Temperature (°C)", min_value=-20, max_value=50, value=20, key="race_temp")
        altitude = st.number_input("Altitude (m)", min_value=0, max_value=3000, value=100, key="race_altitude")
        
        # Calculate average grade
        avg_grade = 100 * (total_elevation / (event_distance * 1000)) if event_distance > 0 else 0
        st.markdown(f"**Average Grade:** {avg_grade:.2f}%")
        
        # Calculate air density
        air_density = AIR_DENSITY_SEA_LEVEL * math.exp(-altitude/8000) * (273/(273+temperature))
        
    with col2:
        st.markdown("#### Position & Equipment")
        
        # Position selection and CdA
        position_options = [
            "Hoods - Relaxed",
            "Hoods - Regular",
            "Drops - Regular",
            "Drops - Tucked",
            "Aero bars",
            "TT position",
            "TT PRO position"
        ]
        race_position = st.selectbox("Race position", position_options, key="race_position")
        
        # Default CdA values based on position
        default_cda = {
            "Hoods - Relaxed": 0.400,
            "Hoods - Regular": 0.350,
            "Drops - Regular": 0.320,
            "Drops - Tucked": 0.300,
            "Aero bars": 0.270,
            "TT position": 0.230,
            "TT PRO position": 0.190
        }
        
        race_cda = st.number_input("CdA override", min_value=0.15, max_value=0.8, value=default_cda[race_position], step=0.005, key="race_cda")
        
        # Rolling resistance and tire selection
        tire_options = [
            "Fast TT tire (0.0025)",
            "Race tire (0.0033)",
            "Race tire (0.0035)",
            "Training tire (0.0040)",
            "Gravel tire (0.0050)",
            "MTB tire (0.0070)"
        ]
        race_tire = st.selectbox("Tire type", tire_options, key="race_tire")
        
        # Default Crr values based on tire type
        default_crr = {
            "Fast TT tire (0.0025)": 0.0025,
            "Race tire (0.0033)": 0.0033,
            "Race tire (0.0035)": 0.0035,
            "Training tire (0.0040)": 0.0040,
            "Gravel tire (0.0050)": 0.0050,
            "MTB tire (0.0070)": 0.0070
        }
        
        race_crr = st.number_input("Crr override", min_value=0.0010, max_value=0.0120, value=default_crr[race_tire], 
                                  step=0.0001, format="%.4f", key="race_crr")
        
        # Drivetrain efficiency
        drivetrain_efficiency_race = st.number_input("Drive train efficiency (%)", min_value=90.0, max_value=100.0, value=97.5, step=0.5, key="drive_eff_race")
        
        st.markdown("#### Predictions")
        
        # Basic power estimation based on event type
        if event_type == "Time trial":
            power_percent = 0.95
        elif event_type == "Road race":
            power_percent = 0.85
        elif event_type == "Criterium":
            power_percent = 0.90
        else:  # Gran fondo
            power_percent = 0.80
                
        sustainable_power = ftp_race * power_percent
        
        # Convert wind speed to m/s
        wind_speed_ms = wind_speed / 3.6
        
        # Calculate speed using the physics-based model from tab1
        def calculate_speed(power, total_weight, grade, cda, crr, wind_speed_ms, air_density, drivetrain_efficiency):
            # Adjust power for drivetrain efficiency
            power_at_wheel = power * (drivetrain_efficiency / 100)
            
            # Function to find speed given power
            def power_diff(speed_ms):
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
                required_power = f_total * speed_ms
                
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
        
        # Calculate the estimated speed using proper physics
        speed_ms = calculate_speed(sustainable_power, total_weight_race, avg_grade, race_cda, race_crr, wind_speed_ms, air_density, drivetrain_efficiency_race)
        estimated_speed = speed_ms * 3.6  # Convert to km/h
        
        # Time calculation
        time_hours = event_distance / estimated_speed if estimated_speed > 0 else 0
        hours = int(time_hours)
        minutes = int((time_hours - hours) * 60)
        seconds = int(((time_hours - hours) * 60 - minutes) * 60)
        estimated_time = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        
        # Display results
        st.markdown(f"**Sustainable power:** {sustainable_power:.0f} watts ({power_percent*100:.0f}% of FTP)")
        st.markdown(f"**Estimated average speed:** {estimated_speed:.1f} km/h")
        st.markdown(f"**Estimated finish time:** {estimated_time}")
            
        # Simple pacing advice
        st.markdown("#### Pacing Advice")
        st.markdown(f"- **Start:** {sustainable_power * 1.05:.0f} watts (first few minutes)")
        st.markdown(f"- **Middle:** {sustainable_power:.0f} watts (maintain steady effort)")
        st.markdown(f"- **Finish:** {sustainable_power * 1.03:.0f} watts (if you feel strong)")
    
    # Calculate normalized power and TSS
    intensity_factor = sustainable_power / ftp_race if ftp_race > 0 else 0
    normalized_power = sustainable_power  # Simplified for steady state
    training_stress_score = (time_hours * 3600) * (normalized_power / ftp_race) ** 2 * 100 / 3600 if ftp_race > 0 else 0
    
    # Display additional metrics
    metrics_col1, metrics_col2 = st.columns(2)
    
    with metrics_col1:
        st.markdown("#### Additional Metrics")
        st.markdown(f"**Intensity Factor:** {intensity_factor:.2f} IF")
        st.markdown(f"**Training Stress Score:** {training_stress_score:.1f} TSS")
    
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
