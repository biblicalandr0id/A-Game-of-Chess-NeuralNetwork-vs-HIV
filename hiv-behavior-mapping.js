// HIV Molecular Behavior to Chess Mapping Analysis
import _ from 'lodash';

const molecularBehaviors = {
  surfaceProteinBinding: {
    biologicalDescription: "Surface proteins attach to CD4 receptors",
    energyCost: "moderate",
    timescale: "seconds",
    chessMapping: {
      piece: "queen", // Surface Protein Complex
      moveType: "diagonal_and_straight",
      specialAbility: "protein_shift",
      energyCost: 3,
      constraints: ["must_be_adjacent", "requires_target"]
    }
  },
  
  rnaTranscription: {
    biologicalDescription: "Viral RNA converts to DNA and integrates",
    energyCost: "high",
    timescale: "hours",
    chessMapping: {
      piece: "bishop", // RNA Strand
      moveType: "diagonal_only",
      specialAbility: "replication",
      energyCost: 5,
      constraints: ["requires_cell_territory", "one_per_turn"]
    }
  },
  
  mutationEvent: {
    biologicalDescription: "Virus undergoes genetic mutation",
    energyCost: "very_high",
    timescale: "generations",
    chessMapping: {
      piece: "knight", // Mutation Vector
      moveType: "l_shape",
      specialAbility: "change_pattern",
      energyCost: 8,
      constraints: ["once_per_three_turns", "must_have_energy"]
    }
  },
  
  viralAssembly: {
    biologicalDescription: "New viral particles are assembled",
    energyCost: "high",
    timescale: "hours",
    chessMapping: {
      piece: "rook", // Viral Factory
      moveType: "straight_only",
      specialAbility: "create_pawn",
      energyCost: 6,
      constraints: ["requires_resources", "limited_per_game"]
    }
  }
};

// Validate that molecular behaviors map to game mechanics
function validateBehaviorMapping() {
  const validations = [];
  
  for (const [behavior, data] of Object.entries(molecularBehaviors)) {
    // Check energy costs are proportional
    const biologicalEnergyCost = energyCostToNumber(data.energyCost);
    const gameEnergyCost = data.chessMapping.energyCost;
    const energyProportional = Math.abs(biologicalEnergyCost - gameEnergyCost/2) < 2;
    
    // Check timescale restrictions
    const hasAppropriateConstraints = validateTimescaleConstraints(
      data.timescale, 
      data.chessMapping.constraints
    );
    
    validations.push({
      behavior,
      isValid: energyProportional && hasAppropriateConstraints,
      issues: []
    });
  }
  
  return validations;
}

// Helper function to convert energy cost strings to numbers
function energyCostToNumber(costString) {
  const costMap = {
    'low': 1,
    'moderate': 3,
    'high': 6,
    'very_high': 8
  };
  return costMap[costString] || 0;
}

// Validate that game constraints reflect biological timescales
function validateTimescaleConstraints(timescale, constraints) {
  const timescaleRequirements = {
    'seconds': ['must_be_adjacent', 'requires_target'],
    'minutes': ['requires_cell_territory'],
    'hours': ['one_per_turn', 'requires_resources'],
    'generations': ['once_per_three_turns']
  };
  
  const requiredConstraints = timescaleRequirements[timescale] || [];
  return requiredConstraints.every(req => constraints.includes(req));
}

// Analyze the mapping coverage
function analyzeMappingCoverage() {
  const totalBehaviors = Object.keys(molecularBehaviors).length;
  const mappedMoves = _.uniq(
    Object.values(molecularBehaviors)
      .map(b => b.chessMapping.moveType)
  ).length;
  
  const coverage = {
    totalBehaviors,
    mappedMoves,
    coveragePercent: (mappedMoves / totalBehaviors) * 100,
    unmappedBehaviors: []
  };
  
  // Find any behaviors without complete mappings
  for (const [behavior, data] of Object.entries(molecularBehaviors)) {
    if (!data.chessMapping || !data.chessMapping.moveType) {
      coverage.unmappedBehaviors.push(behavior);
    }
  }
  
  return coverage;
}

// Run analysis
console.log("Behavior Mapping Validation:", validateBehaviorMapping());
console.log("Mapping Coverage Analysis:", analyzeMappingCoverage());