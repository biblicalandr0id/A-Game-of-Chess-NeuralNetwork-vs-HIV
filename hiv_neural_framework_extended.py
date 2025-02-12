import torch
import torch.nn as nn
import numpy as np
from dataclasses import dataclass
from typing import Dict, List, Tuple
from enum import Enum

class MolecularFeatures(Enum):
    """
    Enumeration of molecular features mapped to state space
    """
    # T-Cell Features (64 protein + 32 membrane + 32 vesicle = 128)
    CD4_DENSITY = "cd4_receptor_density"  # surface density of CD4 receptors
    MEMBRANE_FLUIDITY = "membrane_fluidity"  # lipid bilayer characteristics
    CORECEPTOR_STATUS = "coreceptor_status"  # CCR5/CXCR4 availability
    VESICLE_COUNT = "vesicle_count"  # number of transport vesicles
    ATP_LEVEL = "atp_concentration"  # cellular energy state
    
    # HIV Features (64 surface + 32 RNA + 32 binding = 128)
    ENV_PROTEIN_STATE = "env_protein_conformation"  # gp120/gp41 state
    RNA_INTEGRITY = "viral_rna_integrity"  # genetic material state
    REVERSE_TRANSCRIPTASE = "rt_activity"  # enzyme activity level
    CAPSID_STABILITY = "capsid_stability"  # viral core integrity
    
    # Immune Features (64 antibody + 32 recognition + 32 attack = 128)
    ANTIBODY_SPECIFICITY = "antibody_binding_sites"  # binding characteristics
    MEMORY_CELL_STATUS = "immune_memory_state"  # learned responses
    CYTOKINE_LEVELS = "cytokine_concentration"  # immune signaling

@dataclass
class MolecularState:
    """
    Detailed molecular state representation with biological constraints
    """
    def __init__(self):
        self.features: Dict[MolecularFeatures, float] = {}
        self.constraints = {
            MolecularFeatures.CD4_DENSITY: (0, 1000),  # receptors/μm²
            MolecularFeatures.MEMBRANE_FLUIDITY: (0.1, 1.0),  # relative scale
            MolecularFeatures.ATP_LEVEL: (1, 10)  # mM
        }
    
    def validate_state(self) -> bool:
        """Ensures biological constraints are met"""
        return all(
            self.constraints.get(feature, (float('-inf'), float('inf')))[0] 
            <= value <= 
            self.constraints.get(feature, (float('-inf'), float('inf')))[1]
            for feature, value in self.features.items()
        )

class ChessMolecularAction:
    """
    Maps chess moves to molecular actions with biological constraints
    """
    def __init__(self):
        self.move_to_molecular = {
            # Queen moves (long-range, high energy)
            "queen_diagonal": {
                "molecular_action": "surface_protein_rearrangement",
                "energy_cost": 5,
                "time_scale": 0.1,  # seconds
                "success_rate": 0.85
            },
            # Bishop moves (diagonal patterns)
            "bishop_move": {
                "molecular_action": "membrane_fusion",
                "energy_cost": 3,
                "time_scale": 1.0,  # seconds
                "success_rate": 0.75
            },
            # Knight moves (conformational changes)
            "knight_jump": {
                "molecular_action": "protein_conformation_change",
                "energy_cost": 4,
                "time_scale": 0.5,  # seconds
                "success_rate": 0.70
            }
        }
        
        self.molecular_constraints = {
            "energy_threshold": 10,  # ATP molecules required
            "timing_constraints": (0.1, 10.0),  # seconds
            "spatial_constraints": (1, 100)  # nanometers
        }

class PPOTrainer:
    """
    Proximal Policy Optimization implementation for HIV chess
    """
    def __init__(
        self,
        network: nn.Module,
        learning_rate: float = 3e-4,
        clip_epsilon: float = 0.2,
        value_coef: float = 0.5,
        entropy_coef: float = 0.01
    ):
        self.network = network
        self.optimizer = torch.optim.Adam(network.parameters(), lr=learning_rate)
        self.clip_epsilon = clip_epsilon
        self.value_coef = value_coef
        self.entropy_coef = entropy_coef

    def compute_gae(
        self,
        rewards: torch.Tensor,
        values: torch.Tensor,
        dones: torch.Tensor,
        gamma: float = 0.99,
        lam: float = 0.95
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Compute Generalized Advantage Estimation
        """
        advantages = torch.zeros_like(rewards)
        gae = 0
        
        for t in reversed(range(len(rewards))):
            if t == len(rewards) - 1:
                next_value = 0
            else:
                next_value = values[t + 1]
            
            delta = rewards[t] + gamma * next_value * (1 - dones[t]) - values[t]
            gae = delta + gamma * lam * (1 - dones[t]) * gae
            advantages[t] = gae
            
        returns = advantages + values
        return advantages, returns

    def update_policy(
        self,
        states: torch.Tensor,
        actions: torch.Tensor,
        old_log_probs: torch.Tensor,
        advantages: torch.Tensor,
        returns: torch.Tensor
    ) -> Dict[str, float]:
        """
        Update policy using PPO clipped objective
        """
        # Get current policy and value predictions
        new_policy, new_values = self.network(states)
        new_log_probs = torch.log(new_policy.gather(1, actions))
        
        # Compute policy ratio and clipped objective
        ratio = torch.exp(new_log_probs - old_log_probs)
        clipped_ratio = torch.clamp(
            ratio,
            1 - self.clip_epsilon,
            1 + self.clip_epsilon
        )
        
        # Compute losses
        policy_loss = -torch.min(
            ratio * advantages,
            clipped_ratio * advantages
        ).mean()
        
        value_loss = 0.5 * (returns - new_values).pow(2).mean()
        entropy_loss = -torch.mean(
            torch.sum(new_policy * torch.log(new_policy + 1e-10), dim=-1)
        )
        
        # Compute total loss
        total_loss = (
            policy_loss +
            self.value_coef * value_loss -
            self.entropy_coef * entropy_loss
        )
        
        # Update network
        self.optimizer.zero_grad()
        total_loss.backward()
        torch.nn.utils.clip_grad_norm_(self.network.parameters(), 0.5)
        self.optimizer.step()
        
        return {
            "policy_loss": policy_loss.item(),
            "value_loss": value_loss.item(),
            "entropy_loss": entropy_loss.item(),
            "total_loss": total_loss.item()
        }

class MolecularRewardCalculator:
    """
    Calculates rewards based on molecular state transitions
    """
    def __init__(self):
        self.survival_weights = {
            MolecularFeatures.ENV_PROTEIN_STATE: 0.4,
            MolecularFeatures.CAPSID_STABILITY: 0.3,
            MolecularFeatures.ATP_LEVEL: 0.3
        }
        
        self.evasion_weights = {
            MolecularFeatures.ANTIBODY_SPECIFICITY: -0.5,
            MolecularFeatures.MEMBRANE_FLUIDITY: 0.3,
            MolecularFeatures.VESICLE_COUNT: 0.2
        }

    def calculate_survival_probability(
        self,
        molecular_state: MolecularState
    ) -> float:
        """
        Calculate P(survival) based on molecular features
        """
        survival_score = sum(
            self.survival_weights.get(feature, 0) * value
            for feature, value in molecular_state.features.items()
        )
        return torch.sigmoid(torch.tensor(survival_score)).item()

    def calculate_evasion_probability(
        self,
        molecular_state: MolecularState
    ) -> float:
        """
        Calculate P(immune_evasion) based on molecular features
        """
        evasion_score = sum(
            self.evasion_weights.get(feature, 0) * value
            for feature, value in molecular_state.features.items()
        )
        return torch.sigmoid(torch.tensor(evasion_score)).item()

    def calculate_detection_probability(
        self,
        molecular_state: MolecularState
    ) -> float:
        """
        Calculate P(detection) based on immune system state
        """
        immune_features = [
            MolecularFeatures.ANTIBODY_SPECIFICITY,
            MolecularFeatures.MEMORY_CELL_STATUS,
            MolecularFeatures.CYTOKINE_LEVELS
        ]
        
        detection_score = sum(
            molecular_state.features.get(feature, 0)
            for feature in immune_features
        ) / len(immune_features)
        
        return torch.sigmoid(torch.tensor(detection_score)).item()

    def calculate_resource_cost(
        self,
        action: ChessMolecularAction,
        molecular_state: MolecularState
    ) -> float:
        """
        Calculate E(resource_cost) based on action and state
        """
        base_cost = action.move_to_molecular.get(
            action, {"energy_cost": 0}
        )["energy_cost"]
        
        # Scale cost based on ATP availability
        atp_level = molecular_state.features.get(
            MolecularFeatures.ATP_LEVEL,
            5.0
        )
        return base_cost * (1.0 / atp_level)

if __name__ == "__main__":
    # Initialize components
    molecular_state = MolecularState()
    chess_action = ChessMolecularAction()
    reward_calculator = MolecularRewardCalculator()
    
    # Example molecular state
    molecular_state.features = {
        MolecularFeatures.CD4_DENSITY: 500,
        MolecularFeatures.MEMBRANE_FLUIDITY: 0.7,
        MolecularFeatures.ATP_LEVEL: 5,
        MolecularFeatures.ENV_PROTEIN_STATE: 0.8
    }
    
    # Validate and calculate rewards
    if molecular_state.validate_state():
        survival_prob = reward_calculator.calculate_survival_probability(
            molecular_state
        )
        evasion_prob = reward_calculator.calculate_evasion_probability(
            molecular_state
        )
        print(f"Survival Probability: {survival_prob:.3f}")
        print(f"Evasion Probability: {evasion_prob:.3f}")