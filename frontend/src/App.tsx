import { useEffect, useState } from 'react';
import './styles.css';
import { Stride, WallState } from './types';

function App() {
  const [wallConfig, setWallConfig] = useState({
    width: 21,
    height: 32,
    mode: 'optimal-strides',
    bond: 'stretcher'
  });
  const [wallState, setWallState] = useState<WallState | null>(null);
  const [strideState, setStrideState] = useState<Stride | null>(null);
  const [showDialog, setShowDialog] = useState(true);
  const [isLoading, setIsLoading] = useState(false);

  const handleNextBrick = async () => {
    if (!wallState || isLoading) return;
    
    setIsLoading(true);
    try {
      const res = await fetch('http://localhost:8000/api/next');
      const data = await res.json();
      setWallState(data.wall);
      setStrideState(data.stride);
    } catch (err) {
      console.error('Error fetching next brick:', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    const handleKeyPress = (event: KeyboardEvent) => {
      if (event.key === 'Enter') handleNextBrick();
    };

    window.addEventListener('keypress', handleKeyPress);
    return () => window.removeEventListener('keypress', handleKeyPress);
  }, [wallState, isLoading]);

  const initializeWall = async (e: React.FormEvent) => {
    e.preventDefault();
    
    try {
      const response = await fetch('http://localhost:8000/api/init', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(wallConfig),
      });
      setWallState(await response.json());
      setShowDialog(false);
    } catch (err) {
      console.error('Error initializing wall:', err);
    }
  };

  const renderBrick = (brick: any, rowIndex: number, brickIndex: number) => (
    <div
      key={`${rowIndex}-${brickIndex}`}
      className="brick"
      style={{
        width: `${brick.width * 1.33}rem`,
        backgroundColor: brick.placed 
          ? `hsl(${360 - (brick.stride || 0) * 50}, 80%, 50%)`
          : '#e0e0e0',
      }}
    >
      <span className="brick-label">{brick.stride}</span>
    </div>
  );

  return (
    <div className="app">
      {showDialog && (
        <div className="dialog">
          <form onSubmit={initializeWall}>
            <h2>Initialize Wall</h2>
            <div>
              <label>Mode </label>
              <select
                value={wallConfig.mode}
                onChange={(e) => setWallConfig({...wallConfig, mode: e.target.value})}
              >
                <option value="left-to-right">Left to right</option>
                <option value="optimal-strides">Optimal strides</option>
              </select>
            </div>
            <div>
            <label>Bond </label>
              <select
                value={wallConfig.bond}
                onChange={(e) => setWallConfig({...wallConfig, bond: e.target.value})}
              >
                <option value="stretcher">Stretcher</option>
                <option value="flemish">Flemish</option>
                <option value="english">English</option>
                <option value="wildverband">Wildverband</option>
              </select>
            </div>
            <div>
              <label>Width [Half-Bricks] </label>
              <input
                type="number"
                value={wallConfig.width}
                onChange={(e) => setWallConfig({...wallConfig, width: Number(e.target.value)})}
                min="1"
              />
            </div>
            <div>
              <label>Height [Rows] </label>
              <input
                type="number"
                value={wallConfig.height}
                onChange={(e) => setWallConfig({...wallConfig, height: Number(e.target.value)})}
                min="1"
              />
            </div>
            <div className="dimension-label">
              Width [mm] {wallConfig.width * 110 - 10}
            </div>
            <div className="dimension-label">
              Height [mm] {wallConfig.height * 62.5}
            </div>
            <button type="submit">Create Wall</button>
          </form>
        </div>
      )}

      {wallState && (
        <div className="wall">
          {[...wallState.bricks].reverse().map((row, rowIndex) => (
            <div key={rowIndex} className="row">
              {row.map((brick, brickIndex) => renderBrick(brick, rowIndex, brickIndex))}
            </div>
          ))}
          {strideState && (
            <div 
              className="stride-overlay"
              style={{
                position: 'absolute',
                left: `${strideState.origin_x * 1.33}rem`,
                bottom: `${strideState.origin_y * 1.5}rem`,
                width: `${strideState.width * 1.33}rem`,
                height: `${strideState.height * 1.5}rem`,
                border: '3px solid black',
                backgroundColor: 'rgba(255, 0, 0, 0)',
                pointerEvents: 'none',
              }}
            />
          )}
        </div>
      )}

      <div className="controls-container">
        <span className="instruction-text">
          Press ↵ Return to continue
        </span>
        <button 
          className="reset-button" 
          onClick={() => window.location.reload()}
        >
          Reset Wall
        </button>
      </div>

      {wallState?.is_complete && (
        <div className="completion-popup">
          <div className="completion-content">
            <h2>Wall Complete! 🏁</h2>
            <button onClick={() => window.location.reload()}>Reset</button>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;