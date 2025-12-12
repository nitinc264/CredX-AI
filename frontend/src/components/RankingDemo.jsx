import React, { useState, useEffect } from 'react';

export default function RankingDemo() {
  const [weights, setWeights] = useState({
    semantic: 40,
    preference: 0,
    skill_relevance: 40,
    experience: 20
  });
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);

  const normalizeForApi = (w) => {
    const sum = Object.values(w).reduce((a,b)=>a+b,0) || 1;
    return {
      semantic: w.semantic / sum,
      preference: w.preference / sum,
      skill_relevance: w.skill_relevance / sum,
      experience: w.experience / sum
    };
  };

  const callRankApi = async () => {
    setLoading(true);
    const body = {
      text: 'looking for an ml engineer with pytorch and nlp',
      required_skills: ['pytorch','nlp'],
      required_experience: 'mid',
      weights: normalizeForApi(weights),
      top_k: 10
    };
    try {
      const resp = await fetch('/rank', {
        method: 'POST',
        headers: {'Content-Type':'application/json'},
        body: JSON.stringify(body)
      });
      const data = await resp.json();
      setResults(data.results || []);
    } catch (e) {
      console.error('rank api error', e);
      setResults([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(()=>{ callRankApi(); }, []);

  useEffect(()=>{
    const t = setTimeout(callRankApi, 150);
    return ()=>clearTimeout(t);
  }, [weights]);

  const onSlider = (k,v) => setWeights(s=>({...s, [k]: v}));

  return (
    <div style={{maxWidth:800, margin:'1rem auto', padding:20}}>
      <h2>Ranking Demo — Slider Re-ranking</h2>

      <div style={{marginBottom:12}}>
        {Object.keys(weights).map(k=>(
          <div key={k} style={{marginBottom:8}}>
            <label style={{display:'block', marginBottom:4}}>{k} — {weights[k]}</label>
            <input type='range' min='0' max='100' value={weights[k]} onChange={(e)=>onSlider(k, Number(e.target.value))} />
          </div>
        ))}
      </div>

      <button onClick={callRankApi} disabled={loading}>{loading ? 'Ranking...' : 'Refresh'}</button>

      <div style={{marginTop:20}}>
        <h3>Top candidates</h3>
        {results.length===0 && <div>No results</div>}
        <ul>
          {results.map(r=>(
            <li key={r.id} style={{padding:8, border:'1px solid #ddd', marginBottom:6}}>
              <strong>{r.id}</strong> — Score: {Math.round(r.score)}
              <div style={{fontSize:12, color:'#444'}}>{r.meta && r.meta.summary ? r.meta.summary : ''}</div>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}
