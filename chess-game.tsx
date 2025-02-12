import React, { useState, useEffect } from 'react';

// Game piece types and their special abilities
const PIECES = {
  // HIV Forces (Black)
  bk: { symbol: '♔', name: 'HIV Core', abilities: ['stability_control', 'stealth_mode'] },
  bq: { symbol: '♕', name: 'Surface Protein Complex', abilities: ['surface_shift', 'binding_attack', 'protein_shift'] },
  bb: { symbol: '♗', name: 'RNA Strand', abilities: ['protein_synthesis', 'replication'] },
  bn: { symbol: '♘', name: 'Mutation Vector', abilities: ['mutation_burst', 'pattern_change'] },
  br: { symbol: '♖', name: 'Viral Factory', abilities: ['create_pawn', 'protein_synthesis'] },
  bp: { symbol: '♙', name: 'Basic Viral Particle', abilities: ['stealth_mode', 'vesicle_jump'] },
  
  // Immune System (White)
  wk: { symbol: '♚', name: 'Central Immune Memory', abilities: ['detection_pulse', 'memory_formation'] },
  wq: { symbol: '♛', name: 'Antibody Complex', abilities: ['mass_detection', 'binding_block'] },
  wb: { symbol: '♝', name: 'T-Cell Coordinator', abilities: ['coordinate_response', 'mark_target'] },
  wn: { symbol: '♞', name: 'Marker Protein', abilities: ['tag_piece', 'reveal_hidden'] },
  wr: { symbol: '♜', name: 'Immune Response Center', abilities: ['rapid_response', 'area_scan'] },
  wp: { symbol: '♟', name: 'Basic Immune Cell', abilities: ['basic_attack', 'detection'] }
};

const INITIAL_BOARD = [
  ['br', 'bn', 'bb', 'bq', 'bk', 'bb', 'bn', 'br'],
  ['bp', 'bp', 'bp', 'bp', 'bp', 'bp', 'bp', 'bp'],
  Array(8).fill(null),
  Array(8).fill(null),
  Array(8).fill(null),
  Array(8).fill(null),
  ['wp', 'wp', 'wp', 'wp', 'wp', 'wp', 'wp', 'wp'],
  ['wr', 'wn', 'wb', 'wq', 'wk', 'wb', 'wn', 'wr']
];

const HIVChessBoard = () => {
  const [board, setBoard] = useState(INITIAL_BOARD);
  const [selectedPiece, setSelectedPiece] = useState(null);
  const [energyPoints, setEnergyPoints] = useState({ white: 10, black: 10 });
  const [currentPlayer, setCurrentPlayer] = useState('white');
  const [hiddenPieces, setHiddenPieces] = useState(new Set());
  const [taggedPieces, setTaggedPieces] = useState(new Set());
  const [mutatedPieces, setMutatedPieces] = useState(new Set());
  const [turnCount, setTurnCount] = useState(1);
  const [selectedAbility, setSelectedAbility] = useState(null);

  // Validate moves based on piece type and special abilities
  const isValidMove = (from, to, piece) => {
    const dx = Math.abs(to.col - from.col);
    const dy = Math.abs(to.row - from.row);
    
    // Basic move validation
    switch (piece.charAt(1)) {
      case 'k': // King/HIV Core
        return dx <= 1 && dy <= 1;
      case 'q': // Queen/Surface Protein
        return dx === dy || dx === 0 || dy === 0;
      case 'b': // Bishop/RNA Strand
        return dx === dy;
      case 'n': // Knight/Mutation Vector
        return (dx === 2 && dy === 1) || (dx === 1 && dy === 2);
      case 'r': // Rook/Viral Factory
        return dx === 0 || dy === 0;
      case 'p': // Pawn/Basic Particle
        const direction = piece.charAt(0) === 'w' ? -1 : 1;
        return dx === 0 && (dy === 1 * direction || 
          (from.row === (direction === 1 ? 1 : 6) && dy === 2 * direction));
    }
    return false;
  };

  // Handle special ability activation
  const activateAbility = (ability, piece, position) => {
    const cost = getAbilityCost(ability);
    if (energyPoints[currentPlayer] >= cost) {
      switch (ability) {
        case 'stealth_mode':
          setHiddenPieces(new Set([...hiddenPieces, `${position.row},${position.col}`]));
          break;
        case 'mutation_burst':
          setMutatedPieces(new Set([...mutatedPieces, `${position.row},${position.col}`]));
          break;
        case 'tag_piece':
          setTaggedPieces(new Set([...taggedPieces, `${position.row},${position.col}`]));
          break;
        // Add more ability implementations
      }
      setEnergyPoints({
        ...energyPoints,
        [currentPlayer]: energyPoints[currentPlayer] - cost
      });
    }
  };

  // Get ability cost based on biological parameters
  const getAbilityCost = (ability) => {
    const costs = {
      'stealth_mode': 5,
      'mutation_burst': 7,
      'surface_shift': 4,
      'protein_synthesis': 6,
      'tag_piece': 3,
      // Add more ability costs
    };
    return costs[ability] || 1;
  };

  // Update energy points each turn
  useEffect(() => {
    const energyPerTurn = 2;
    setEnergyPoints(prev => ({
      ...prev,
      [currentPlayer]: prev[currentPlayer] + energyPerTurn
    }));
  }, [currentPlayer]);

  const handleSquareClick = (row, col) => {
    const piece = board[row][col];
    
    if (selectedAbility) {
      // Handle ability usage
      if (piece && piece.charAt(0) === currentPlayer.charAt(0)) {
        activateAbility(selectedAbility, piece, { row, col });
        setSelectedAbility(null);
      }
      return;
    }

    if (!selectedPiece && piece) {
      const pieceColor = piece.charAt(0) === 'w' ? 'white' : 'black';
      if (pieceColor === currentPlayer) {
        setSelectedPiece({ row, col, piece });
      }
    } else if (selectedPiece) {
      if (isValidMove(selectedPiece, { row, col }, selectedPiece.piece)) {
        const newBoard = board.map(row => [...row]);
        newBoard[row][col] = selectedPiece.piece;
        newBoard[selectedPiece.row][selectedPiece.col] = null;
        setBoard(newBoard);
        setCurrentPlayer(currentPlayer === 'white' ? 'black' : 'white');
        setTurnCount(turnCount + 1);
      }
      setSelectedPiece(null);
    }
  };

  // Render ability buttons for selected piece
  const renderAbilityButtons = () => {
    if (!selectedPiece) return null;
    const pieceAbilities = PIECES[selectedPiece.piece].abilities;
    
    return (
      <div className="mt-4 flex flex-wrap gap-2">
        {pieceAbilities.map(ability => (
          <button
            key={ability}
            className={`px-3 py-1 rounded ${
              selectedAbility === ability ? 'bg-blue-500' : 'bg-gray-200'
            } hover:bg-blue-300`}
            onClick={() => setSelectedAbility(ability)}
          >
            {ability.replace('_', ' ')} ({getAbilityCost(ability)} energy)
          </button>
        ))}
      </div>
    );
  };

  return (
    <div className="flex flex-col items-center p-4">
      <div className="mb-4">
        <div className="text-lg font-bold mb-2">Energy Points</div>
        <div>White: {energyPoints.white} | Black: {energyPoints.black}</div>
        <div>Turn: {turnCount}</div>
      </div>
      
      <div className="grid grid-cols-8 gap-0 border border-gray-400">
        {board.map((row, rowIndex) => (
          row.map((piece, colIndex) => {
            const isLight = (rowIndex + colIndex) % 2 === 0;
            const isSelected = selectedPiece && 
              selectedPiece.row === rowIndex && 
              selectedPiece.col === colIndex;
            const isHidden = hiddenPieces.has(`${rowIndex},${colIndex}`);
            const isTagged = taggedPieces.has(`${rowIndex},${colIndex}`);
            const isMutated = mutatedPieces.has(`${rowIndex},${colIndex}`);
            
            return (
              <div
                key={`${rowIndex}-${colIndex}`}
                className={`
                  w-16 h-16 flex items-center justify-center text-3xl
                  ${isLight ? 'bg-gray-200' : 'bg-gray-400'}
                  ${isSelected ? 'bg-yellow-200' : ''}
                  ${isHidden ? 'opacity-50' : ''}
                  ${isTagged ? 'border-2 border-red-500' : ''}
                  ${isMutated ? 'bg-purple-200' : ''}
                  cursor-pointer
                  hover:bg-blue-200
                `}
                onClick={() => handleSquareClick(rowIndex, colIndex)}
              >
                {piece && PIECES[piece].symbol}
              </div>
            );
          })
        ))}
      </div>

      {renderAbilityButtons()}

      <div className="mt-4">
        <div className="text-lg font-bold">Current Player: {currentPlayer}</div>
      </div>
    </div>
  );
};

export default HIVChessBoard;