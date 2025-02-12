from enum import Enum
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional
import numpy as np

class MolecularFeatures(Enum):
    """Comprehensive molecular features for HIV-immune system interaction"""
    
    # T-Cell Features (128 total)
    CD4_DENSITY = "cd4_receptor_density"
    """Surface density of CD4 receptors (receptors/μm²).
    Critical for initial HIV binding. Normal range: 100-1000/μm².
    Higher density increases infection probability."""
    
    MEMBRANE_FLUIDITY = "membrane_fluidity"
    """Lipid bilayer fluidity (0-1 scale).
    Affects fusion efficiency and receptor mobility.
    Temperature and cholesterol dependent."""
    
    CORECEPTOR_STATUS = "coreceptor_status"
    """CCR5/CXCR4 availability (ratio).
    Determines viral tropism and entry efficiency.
    Key factor in R5/X4 strain susceptibility."""
    
    VESICLE_COUNT = "vesicle_count"
    """Number of transport vesicles.
    Influences viral particle trafficking.
    Normal range: 10-100 per cell."""
    
    ATP_LEVEL = "atp_concentration"
    """Cellular energy state (mM).
    Powers viral processes and immune responses.
    Critical threshold: 1-10 mM."""
    
    T_CELL_ACTIVATION = "t_cell_activation_level"
    """T-cell activation state (0-1 scale).
    Higher activation increases viral replication.
    Influences cytokine production."""
    
    # HIV Features (128 total)
    ENV_PROTEIN_STATE = "env_protein_conformation"
    """gp120/gp41 conformational state.
    Determines binding efficiency and immune evasion.
    Multiple conformational states possible."""
    
    RNA_INTEGRITY = "viral_rna_integrity"
    """Genetic material state (0-1 scale).
    Affects replication fidelity and drug resistance.
    Mutation rate: ~3x10^-5 per base per cycle."""
    
    REVERSE_TRANSCRIPTASE = "rt_activity"
    """RT enzyme activity level (0-1 scale).
    Critical for viral genome replication.
    Target of NRTI/NNRTI drugs."""
    
    CAPSID_STABILITY = "capsid_stability"
    """Viral core integrity (0-1 scale).
    Influences uncoating timing and efficiency.
    Temperature and pH dependent."""
    
    VIRAL_LOAD = "viral_load"
    """Viral particles per mL.
    Key clinical marker of infection progress.
    Normal range: 40-10^6 copies/mL."""
    
    REPLICATION_RATE = "replication_rate"
    """New virions produced per day.
    Affected by cell activation and resources.
    Typical range: 10^8-10^9 per day."""
    
    DRUG_RESISTANCE = "drug_resistance_mutations"
    """Presence of resistance mutations (0-1 scale).
    Affects treatment efficacy.
    Multiple resistance pathways possible."""
    
    # Immune Features (128 total)
    ANTIBODY_SPECIFICITY = "antibody_binding_sites"
    """Antibody binding characteristics.
    Determines neutralization efficiency.
    Evolves during infection."""
    
    MEMORY_CELL_STATUS = "immune_memory_state"
    """Learned immune responses (0-1 scale).
    Affects recognition speed and specificity.
    Builds over infection course."""
    
    CYTOKINE_LEVELS = "cytokine_concentration"
    """Immune signaling molecules (pg/mL).
    Coordinates immune response.
    Multiple cytokine types tracked."""
    
    INTERFERON_RESPONSE = "interferon_levels"
    """Type I/II interferon activity.
    Crucial for antiviral state induction.
    Measured in International Units/mL."""
    
    NK_CELL_ACTIVITY = "natural_killer_activity"
    """NK cell cytotoxic activity (0-1 scale).
    Early response to viral infection.
    Cytokine-dependent activation."""

@dataclass
class MolecularState:
    """
    Comprehensive molecular state representation with biological constraints
    and initialization parameters
    """
    def __init__(self, random_init: bool = False):
        self.features: Dict[MolecularFeatures, float] = {}
        self.constraints = {
            MolecularFeatures.CD4_DENSITY: {
                "range": (100, 1000),  # receptors/μm²
                "description": "Normal T-cell surface density range",
                "critical_threshold": 200  # Min for viable infection
            },
            MolecularFeatures.MEMBRANE_FLUIDITY: {
                "range": (0.1, 1.0),
                "description": "Normalized fluidity scale",
                "optimal_range": (0.4, 0.6)  # Best for fusion
            },
            MolecularFeatures.ATP_LEVEL: {
                "range": (1, 10),  # mM
                "description": "Cellular ATP concentration",
                "critical_threshold": 2  # Min for viral processes
            },
            MolecularFeatures.VIRAL_LOAD: {
                "range": (40, 1e6),  # copies/mL
                "description": "Clinical viral load range",
                "detection_threshold": 40
            },
            MolecularFeatures.INTERFERON_RESPONSE: {
                "range": (0, 1000),  # IU/mL
                "description": "Interferon activity level",
                "effective_threshold": 100
            }
        }
        
        if random_init:
            self.initialize_random_state()
    
    def initialize_random_state(self) -> None:
        """
        Initialize state with random but biologically plausible values
        """
        for feature in MolecularFeatures:
            if feature in self.constraints:
                min_val, max_val = self.constraints[feature]["range"]
                # Use truncated normal distribution for more realistic values
                mean = (min_val + max_val) / 2
                std = (max_val - min_val) / 6  # 99.7% within range
                value = np.random.normal(mean, std)
                value = np.clip(value, min_val, max_val)
                self.features[feature] = value
            else:
                # Default to normalized range for unconstrained features
                self.features[feature] = np.random.random()
    
    def validate_state(self) -> Tuple[bool, List[str]]:
        """
        Ensures biological constraints are met
        Returns: (is_valid, list of violations)
        """
        violations = []
        for feature, value in self.features.items():
            if feature in self.constraints:
                min_val, max_val = self.constraints[feature]["range"]
                if value < min_val or value > max_val:
                    violations.append(
                        f"{feature.value}: {value} outside range [{min_val}, {max_val}]"
                    )
                    
                if "critical_threshold" in self.constraints[feature]:
                    threshold = self.constraints[feature]["critical_threshold"]
                    if value < threshold:
                        violations.append(
                            f"{feature.value}: {value} below critical threshold {threshold}"
                        )
        
        return len(violations) == 0, violations
    
    def get_feature_description(self, feature: MolecularFeatures) -> str:
        """
        Get biological description and constraints for a feature
        """
        description = feature.value
        if feature in self.constraints:
            constraints = self.constraints[feature]
            description += f"\nRange: {constraints['range']}"
            description += f"\nDescription: {constraints['description']}"
            if "critical_threshold" in constraints:
                description += f"\nCritical threshold: {constraints['critical_threshold']}"
            if "optimal_range" in constraints:
                description += f"\nOptimal range: {constraints['optimal_range']}"
        return description

if __name__ == "__main__":
    # Example usage and validation
    state = MolecularState(random_init=True)
    is_valid, violations = state.validate_state()
    
    print("Initial Molecular State:")
    for feature, value in state.features.items():
        print(f"\n{feature.name}:")
        print(state.get_feature_description(feature))
        print(f"Current value: {value}")
    
    print("\nValidation Results:")
    print(f"Valid state: {is_valid}")
    if not is_valid:
        print("Violations:")
        for violation in violations:
            print(f"- {violation}")