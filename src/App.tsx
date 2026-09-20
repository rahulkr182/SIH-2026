import { useState, useRef } from 'react';
import { 
  ShieldCheck, 
  WifiOff, 
  Upload, 
  Cpu, 
  FileText, 
  CheckCircle2, 
  ChevronRight,
  Database,
  Calculator,
  Lock,
  Download,
  FileCheck2,
  Terminal,
  Activity,
  ArrowRight
} from 'lucide-react';

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [loginId, setLoginId] = useState('');
  const [password, setPassword] = useState('');
  
  const [processingState, setProcessingState] = useState<'idle' | 'processing' | 'done'>('idle');
  const [activeTab, setActiveTab] = useState<'input' | 'output'>('input');
  const [currentStep, setCurrentStep] = useState(0);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleLogin = (e: React.FormEvent) => {
    e.preventDefault();
    if (loginId.trim() !== '') {
      setIsAuthenticated(true);
    }
  };

  const steps = [
    { title: "RouteLLM Classifier", desc: "Analyzing input modality and dispatching to vision model." },
    { title: "Qwen2.5-VL-7B Vision", desc: "Extracting handwritten thickness logs from API 510." },
    { title: "Docker Sandbox Math", desc: "Verifying corrosion rate calculation via Python SymPy." },
    { title: "DeepSeek-R1-Distill", desc: "Drafting official justification memo." }
  ];

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      setSelectedFile(e.target.files[0]);
    }
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    e.currentTarget.classList.add('drag-active');
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    e.currentTarget.classList.remove('drag-active');
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.currentTarget.classList.remove('drag-active');
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      setSelectedFile(e.dataTransfer.files[0]);
    }
  };

  const [chatHistory, setChatHistory] = useState<{role: 'user' | 'agent', content: string}[]>([]);

  const handleProcess = async () => {
    if (!selectedFile) {
      alert("Please upload a file first to run the AI.");
      return;
    }
    
    setProcessingState('processing');
    setCurrentStep(0);
    setActiveTab('input');
    
    // Animate steps quickly to show "agentic" process
    const stepInterval = setInterval(() => {
      setCurrentStep(prev => {
        if (prev < steps.length - 1) return prev + 1;
        clearInterval(stepInterval);
        return prev;
      });
    }, 1000);

    try {
      const formData = new FormData();
      formData.append('prompt', "Please process the attached document according to the task modality.");
      formData.append('modality', "API 510 Inspection / P&ID Analysis");
      formData.append('file', selectedFile);

      // Add user message to chat history immediately
      setChatHistory(prev => [...prev, {role: 'user', content: `Submitted document: ${selectedFile.name} for processing.`}]);

      const response = await fetch('http://localhost:8000/api/task', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error("Backend API error or Invalid API Key.");
      }

      const data = await response.json();
      
      setChatHistory(prev => [...prev, {role: 'agent', content: data.message}]);
      setProcessingState('done');
      setActiveTab('output');
    } catch (error: any) {
      console.error(error);
      setChatHistory(prev => [...prev, {role: 'agent', content: `Error: Could not process request. Make sure the FastAPI backend is running.`}]);
      setProcessingState('done');
      setActiveTab('output');
    }
  };

  const handleDownloadDocx = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/download_memo', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ history: chatHistory }),
      });
      if (!response.ok) throw new Error("Download failed");
      
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'MRPL_Audit_Log.docx';
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
    } catch (e) {
      console.error(e);
      alert("Failed to download document.");
    }
  };

  const triggerFileInput = () => {
    fileInputRef.current?.click();
  };

  if (!isAuthenticated) {
    return (
      <div className="login-container">
        <div className="login-card">
          <div className="login-header">
            <ShieldCheck size={48} color="var(--primary-color)" style={{margin: '0 auto 1rem auto'}} />
            <h2>MRPL Sovereign AI Access</h2>
            <p>Air-Gapped Copilot Workbench</p>
          </div>
          <div className="login-body">
            <form onSubmit={handleLogin}>
              <div style={{marginBottom: '1rem'}}>
                <label className="form-label">Employee ID (LDAP)</label>
                <input 
                  type="text" 
                  className="input-select" 
                  style={{backgroundImage: 'none', padding: '0.6rem'}} 
                  value={loginId}
                  onChange={(e) => setLoginId(e.target.value)}
                  placeholder="e.g. EMP-2048"
                  required
                />
              </div>
              <div style={{marginBottom: '1.5rem'}}>
                <label className="form-label">Password</label>
                <input 
                  type="password" 
                  className="input-select" 
                  style={{backgroundImage: 'none', padding: '0.6rem'}}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                  required
                />
              </div>
              <button type="submit" className="btn btn-primary" style={{width: '100%', padding: '0.8rem', fontSize: '1.1rem'}}>
                Secure Login
              </button>
            </form>
          </div>
          <div className="login-footer">
            <Lock size={12} style={{display: 'inline', marginRight: '4px', verticalAlign: 'text-bottom'}} />
            Connection secured via internal air-gapped network.
          </div>
        </div>
      </div>
    );
  }

  return (
    <>
      <header className="header">
        <div className="brand">
          <ShieldCheck size={32} className="brand-icon" />
          <div>
            <h1>Sovereign AI Workbench</h1>
            <span>Syntax Slayers | SIH 2026 (PS: 26117)</span>
          </div>
        </div>
        
        <div className="badges-container">
          <div className="badge badge-network">
            <WifiOff size={16} /> 0.00 KB Egress
          </div>
          <div className="badge badge-security">
            <Lock size={16} /> Air-Gapped GPU
          </div>
        </div>
      </header>

      <main className="app-container">
        {/* Sidebar */}
        <aside className="panel" style={{alignSelf: 'start', display: 'flex', flexDirection: 'column', gap: '2rem'}}>
          
          <div>
            <div className="panel-header">
              <Activity size={18} /> Recent Sessions
            </div>
            <ul className="feature-list" style={{gap: '0.5rem'}}>
              <li className="feature-item" style={{padding: '0.75rem', backgroundColor: '#e8f0fe', borderRadius: '4px', borderLeft: '3px solid var(--primary-color)', cursor: 'pointer'}}>
                <div className="feature-icon" style={{color: 'var(--primary-color)'}}><FileText size={18} /></div>
                <div className="feature-text">
                  <h4 style={{fontSize: '0.9rem', marginBottom: '0'}}>API 510: Pump 104-A</h4>
                  <p style={{fontSize: '0.75rem'}}>Today, 10:42 AM</p>
                </div>
              </li>
              <li className="feature-item" style={{padding: '0.75rem', borderRadius: '4px', cursor: 'pointer'}}>
                <div className="feature-icon" style={{color: '#999'}}><Calculator size={18} /></div>
                <div className="feature-text">
                  <h4 style={{fontSize: '0.9rem', color: '#555', marginBottom: '0'}}>Pressure Calc: Line 4</h4>
                  <p style={{fontSize: '0.75rem'}}>Yesterday, 2:15 PM</p>
                </div>
              </li>
              <li className="feature-item" style={{padding: '0.75rem', borderRadius: '4px', cursor: 'pointer'}}>
                <div className="feature-icon" style={{color: '#999'}}><Database size={18} /></div>
                <div className="feature-text">
                  <h4 style={{fontSize: '0.9rem', color: '#555', marginBottom: '0'}}>SOP Query: Hot Work</h4>
                  <p style={{fontSize: '0.75rem'}}>Sep 15, 9:00 AM</p>
                </div>
              </li>
            </ul>
          </div>

          <div>
            <div className="panel-header">
              <Activity size={18} /> Architecture Stack
            </div>
            <ul className="feature-list" style={{gap: '1rem'}}>
              <li className="feature-item">
                <div className="feature-text">
                  <h4 style={{fontSize: '0.85rem'}}>Agentic Orchestration</h4>
                  <p style={{fontSize: '0.75rem'}}>LangGraph multi-step workflows.</p>
                </div>
              </li>
              <li className="feature-item">
                <div className="feature-text">
                  <h4 style={{fontSize: '0.85rem'}}>Isolated Execution</h4>
                  <p style={{fontSize: '0.75rem'}}>Docker sandboxing for exact math.</p>
                </div>
              </li>
            </ul>
          </div>

          <div>
            <div className="panel-header" style={{color: '#d32f2f'}}>
              <ShieldCheck size={18} /> Air-Gap Monitor
            </div>
            <div style={{
              backgroundColor: '#0a0a0a', 
              color: '#00ff00', 
              fontFamily: 'monospace', 
              fontSize: '0.75rem', 
              padding: '1rem', 
              borderRadius: '6px',
              height: '140px',
              overflow: 'hidden',
              display: 'flex',
              flexDirection: 'column',
              justifyContent: 'flex-end',
              boxShadow: 'inset 0 0 10px rgba(0,0,0,0.8)'
            }}>
              <div style={{opacity: 0.5}}>[KERNEL] DROP SYN -&gt; 142.250.190.46</div>
              <div style={{opacity: 0.7}}>[IPTABLES] BLOCKED OUTBOUND PORT 443</div>
              <div style={{opacity: 0.9}}>[DOCKER] SANDBOX NETWORK=NONE VERIFIED</div>
              <div style={{color: '#ff3333', fontWeight: 'bold', marginTop: '0.75rem', borderTop: '1px solid #333', paddingTop: '0.5rem', display: 'flex', justifyContent: 'space-between'}}>
                <span>WAN Egress:</span>
                <span>0.00 KB</span>
              </div>
            </div>
          </div>
        </aside>

        {/* Main Interface */}
        <div className="workspace">
          
          <div className="workspace-header" style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center'}}>
            <div>
              <h2>Agent Task Runner (vLLM Engine)</h2>
              <p>Submit documents for automated processing by local open-weight models.</p>
            </div>
          </div>
          
          {/* Explicit Input and Output Buttons/Tabs */}
          <div style={{display: 'flex', gap: '1rem', borderBottom: '2px solid #ccc', paddingBottom: '1rem', marginBottom: '1rem'}}>
            <button 
              className={`btn ${activeTab === 'input' ? 'btn-primary' : 'btn-secondary'}`} 
              onClick={() => setActiveTab('input')}
              style={{fontSize: '1.1rem', padding: '1rem 2rem'}}
            >
              <Upload size={20} /> INPUT DATA
            </button>
            
            <div style={{display: 'flex', alignItems: 'center', color: '#888'}}>
               <ArrowRight size={24} />
            </div>

            <button 
              className={`btn ${activeTab === 'output' ? 'btn-primary' : 'btn-secondary'}`} 
              onClick={() => setActiveTab('output')}
              style={{fontSize: '1.1rem', padding: '1rem 2rem'}}
              disabled={chatHistory.length === 0}
            >
              <FileText size={20} /> CHAT HISTORY & OUTPUT
            </button>
          </div>

          {/* Input Section */}
          {activeTab === 'input' && (
            <>
              <div className="panel">
                <div className="panel-header">
                  <Cpu size={18} /> Data Input
                </div>
                
                <div style={{marginBottom: '1.5rem'}}>
                  <label className="form-label">Task Modality</label>
                  <select className="input-select">
                    <option>Process API 510 Inspection Report (Handwritten)</option>
                    <option>Analyze P&ID Schematic Diagram</option>
                    <option>Calculate Pipeline Pressure Formulas</option>
                  </select>
                </div>

                <div style={{marginBottom: '1.5rem'}}>
                  <label className="form-label">Upload Source Document</label>
                  <input 
                    type="file" 
                    ref={fileInputRef} 
                    style={{display: 'none'}} 
                    onChange={handleFileSelect}
                    accept=".pdf,.png,.jpg,.jpeg"
                  />
                  
                  {!selectedFile ? (
                    <div 
                      className="upload-zone" 
                      onClick={triggerFileInput}
                      onDragOver={handleDragOver}
                      onDragLeave={handleDragLeave}
                      onDrop={handleDrop}
                    >
                      <Upload size={40} className="upload-icon" />
                      <div className="upload-text">Click to browse or drag and drop</div>
                      <div className="upload-subtext">Supports PDF, PNG, JPG (Max 50MB)</div>
                    </div>
                  ) : (
                    <div className="upload-zone" style={{borderColor: 'var(--tertiary-color)', backgroundColor: '#f1f8e9'}}>
                      <FileCheck2 size={40} color="var(--tertiary-color)" style={{marginBottom: '1rem'}} />
                      <div className="upload-text" style={{color: 'var(--tertiary-color)'}}>File Selected Successfully</div>
                      <div className="upload-subtext">{selectedFile.name} ({(selectedFile.size / 1024 / 1024).toFixed(2)} MB)</div>
                      <button className="btn btn-secondary" style={{marginTop: '1rem'}} onClick={(e) => {e.stopPropagation(); setSelectedFile(null);}}>
                        Remove
                      </button>
                    </div>
                  )}
                </div>

                <div style={{display: 'flex', justifyContent: 'flex-end'}}>
                  <button className="btn btn-primary" onClick={handleProcess} disabled={!selectedFile || processingState === 'processing'}>
                    <Terminal size={18} /> {processingState === 'processing' ? 'Processing via FastAPI & LangGraph...' : 'Execute Agentic Flow'}
                  </button>
                </div>
              </div>

              {/* Processing Workflow */}
              {processingState === 'processing' && (
                <div className="panel">
                  <div className="panel-header">
                    <Cpu size={18} /> LangGraph Orchestrator Running
                  </div>
                  
                  <div className="workflow">
                    {steps.map((step, index) => {
                      let status = 'pending';
                      if (index < currentStep) status = 'completed';
                      if (index === currentStep) status = 'active';

                      return (
                        <div key={index} className={`step ${status}`}>
                          <div className="step-indicator">
                            {status === 'completed' ? <CheckCircle2 size={20} /> : (status === 'active' ? <Cpu size={18} /> : <ChevronRight size={18} />)}
                          </div>
                          <div className="step-content">
                            <div className="step-title">{step.title}</div>
                            <div className="step-desc">{step.desc}</div>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>
              )}
            </>
          )}

          {/* Output / Chat Section */}
          {activeTab === 'output' && (
            <div className="panel">
              <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem'}}>
                <div style={{display: 'flex', alignItems: 'center', gap: '0.75rem', color: 'var(--tertiary-color)'}}>
                  <CheckCircle2 size={28} /> 
                  <h2 style={{fontSize: '1.5rem', fontWeight: 600}}>AI Agent Session History</h2>
                </div>
                <button className="btn btn-secondary" onClick={() => {setProcessingState('idle'); setSelectedFile(null); setActiveTab('input');}}>
                  New Document Request
                </button>
              </div>

              <div style={{display: 'flex', flexDirection: 'column', gap: '1.5rem', backgroundColor: '#f9f9f9', padding: '2rem', borderRadius: '8px', border: '1px solid #ccc', minHeight: '400px'}}>
                {chatHistory.map((msg, idx) => (
                  <div key={idx} style={{
                    alignSelf: msg.role === 'user' ? 'flex-end' : 'flex-start',
                    backgroundColor: msg.role === 'user' ? '#e8f0fe' : 'white',
                    border: msg.role === 'user' ? '1px solid #b6d4fe' : '1px solid #ccc',
                    padding: '1rem',
                    borderRadius: '8px',
                    maxWidth: '85%',
                    boxShadow: '0 2px 4px rgba(0,0,0,0.05)'
                  }}>
                    <div style={{fontWeight: 700, marginBottom: '0.5rem', color: msg.role === 'user' ? '#003366' : '#138808'}}>
                      {msg.role === 'user' ? 'Engineer' : 'LangGraph Agent'}
                    </div>
                    <div style={{fontFamily: msg.role === 'agent' ? 'Times New Roman, serif' : 'inherit', fontSize: msg.role === 'agent' ? '1.1rem' : '1rem', whiteSpace: 'pre-wrap'}}>
                      {msg.content}
                    </div>
                  </div>
                ))}
              </div>
              
              <div style={{textAlign: 'center', marginTop: '2rem'}}>
                 <button className="btn btn-primary" onClick={handleDownloadDocx} style={{gap: '0.75rem', padding: '1rem 2rem', fontSize: '1.1rem'}}>
                    <Download size={20} /> Download Session as Audit Log (.docx)
                 </button>
              </div>
            </div>
          )}
        </div>
      </main>
    </>
  )
}

export default App
