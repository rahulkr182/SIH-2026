def api510_corrosion_rate(previous_thickness: float, current_thickness: float, years_between_inspections: float) -> float:
    """
    Calculates the long-term corrosion rate (LTCR) per API 510.
    Returns mm/yr.
    """
    if years_between_inspections <= 0:
        raise ValueError("Years between inspections must be > 0")
    return (previous_thickness - current_thickness) / years_between_inspections

def api510_remaining_life(current_thickness: float, minimum_required_thickness: float, corrosion_rate: float) -> float:
    """
    Calculates remaining life per API 510.
    Returns years.
    """
    if corrosion_rate <= 0:
        return float('inf') # Infinite remaining life if no corrosion
    return (current_thickness - minimum_required_thickness) / corrosion_rate
