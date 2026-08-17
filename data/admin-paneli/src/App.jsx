import React, { useState, useEffect } from 'react';
import './index.css';

const App = () => {
  const [activeTab, setActiveTab] = useState('settings');
  const [activeSettingsCategory, setActiveSettingsCategory] = useState('security'); 
  const [isSaving, setIsSaving] = useState(false);
  
  // 1. ARAMA VE YAPAY ZEKA PARAMETRELERİ
  const [threshold, setThreshold] = useState(0.2);
  const [timeLimit, setTimeLimit] = useState('2_months');
  const [customDays, setCustomDays] = useState(30); 
  const [temperature, setTemperature] = useState(0.2); 
  const [maxTokens, setMaxTokens] = useState('medium'); 
  const [sourceFilter, setSourceFilter] = useState('all'); 

  // 2. GÖRÜNÜM VE ARAYÜZ
  const [accentColor, setAccentColor] = useState('#3b82f6');
  const [themeMode, setThemeMode] = useState('dark');
  const [fontSize, setFontSize] = useState('medium');
  const [chatWidth, setChatWidth] = useState('standard');
  const [aiName, setAiName] = useState('Konya Veri Asistanı');
  const [userNickname, setUserNickname] = useState('Sen');
  const [greetingText, setGreetingText] = useState('Kurumsal RAG Demosu (Admin Panelinden Yönetilmektedir)');
  const [inputPlaceholder, setInputPlaceholder] = useState("RAG motoruna sorunuzu yazın (Enter'a basarak arayın)...");
  const [suggestedPrompts, setSuggestedPrompts] = useState("KOSKİ su faturası nasıl ödenir?, Komek hangi eğitimleri veriyor?, Konya'da son haberler neler?");
  
  // 3. GÜVENLİK VE API (YENİ EKLENEN KURUMSAL ÖZELLİKLER)
  const [apiKey, setApiKey] = useState('');
  const [isEditingApi, setIsEditingApi] = useState(false);
  
  const [killSwitch, setKillSwitch] = useState(false); // Madde 6
  const [profanityFilter, setProfanityFilter] = useState(true); // Madde 2
  const [piiMasking, setPiiMasking] = useState(true); // Madde 3
  const [maxPromptLength, setMaxPromptLength] = useState(500); // Madde 4
  const [rateLimit, setRateLimit] = useState(50); // Madde 4
  const [allowedDomains, setAllowedDomains] = useState("localhost, konya.bel.tr, koski.gov.tr"); // Madde 5

  useEffect(() => {
    document.documentElement.style.setProperty('--accent-color', accentColor);
    if(accentColor === '#8b5cf6') document.body.style.backgroundImage = 'radial-gradient(at 0% 0%, rgba(139, 92, 246, 0.15) 0px, transparent 50%), radial-gradient(at 100% 100%, rgba(59, 130, 246, 0.15) 0px, transparent 50%)';
    else if(accentColor === '#10b981') document.body.style.backgroundImage = 'radial-gradient(at 0% 0%, rgba(16, 185, 129, 0.15) 0px, transparent 50%), radial-gradient(at 100% 100%, rgba(59, 130, 246, 0.15) 0px, transparent 50%)';
    else document.body.style.backgroundImage = 'radial-gradient(at 0% 0%, rgba(59, 130, 246, 0.15) 0px, transparent 50%), radial-gradient(at 100% 100%, rgba(139, 92, 246, 0.15) 0px, transparent 50%)';
  }, [accentColor]);

  const handleSave = async () => {
    setIsSaving(true);
    try {
      await fetch('http://localhost:8000/admin/settings', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          accentColor, threshold, timeLimit: timeLimit === 'custom' ? `${customDays}_days` : timeLimit,
          temperature, maxTokens, sourceFilter, apiKey,
          themeMode, fontSize, chatWidth, aiName, userNickname, greetingText, inputPlaceholder, suggestedPrompts,
          killSwitch, profanityFilter, piiMasking, maxPromptLength, rateLimit, allowedDomains // Yeni Veriler Kargolandı
        })
      });
      alert("✅ Ayarlar başarıyla kaydedildi! Güvenlik kalkanları aktif.");
    } catch (e) {
      alert("❌ Hata! Python sunucusu kapalı olabilir.");
    }
    setIsSaving(false);
  };

  return (
    <div className="app-container">
      <nav className="sidebar glass-panel">
        <div className="logo"><div className="logo-dot"></div>Kurumsal RAG</div>
        <div className="nav-links">
          <button className={`nav-btn ${activeTab === 'settings' ? 'active' : ''}`} onClick={() => setActiveTab('settings')}>
            ⚙️ Sistem Yönetimi
          </button>
        </div>
      </nav>

      <main className="main-content glass-panel" style={{display: 'flex', flexDirection: 'column'}}>
        {activeTab === 'settings' && (
          <div style={{flex: 1, display: 'flex', flexDirection: 'column'}}>
            <h1 className="header-title">Sistem Yapılandırması</h1>
            <p className="header-subtitle">Yapay zeka motorunu, güvenliği ve arayüzü modüler olarak yönetin.</p>
            
            <div className="settings-container" style={{flex: 1, display: 'flex'}}>
              <div className="settings-sidebar">
                <button className={`settings-category-btn ${activeSettingsCategory === 'search' ? 'active' : ''}`} onClick={() => setActiveSettingsCategory('search')}>🔍 Arama ve Filtreleme</button>
                <button className={`settings-category-btn ${activeSettingsCategory === 'appearance' ? 'active' : ''}`} onClick={() => setActiveSettingsCategory('appearance')}>🎨 Görünüm ve Arayüz</button>
                <button className={`settings-category-btn ${activeSettingsCategory === 'security' ? 'active' : ''}`} onClick={() => setActiveSettingsCategory('security')}>🛡️ Güvenlik ve API</button>
              </div>

              <div className="settings-content" style={{overflowY: 'auto', paddingRight: '1rem', flex: 1}}>
                
                {/* 1. ARAMA VE YAPAY ZEKA AYARLARI */}
                {activeSettingsCategory === 'search' && (
                  <div className="card-grid" style={{gridTemplateColumns: '1fr'}}>
                    <h2 className="settings-section-title">Yapay Zeka Parametreleri</h2>
                    <div className="setting-card">
                      <h3>⚖️ Benzerlik Eşiği (Threshold)</h3>
                      <input type="range" min="0" max="1" step="0.05" value={threshold} onChange={(e) => setThreshold(parseFloat(e.target.value))} />
                    </div>
                    <div className="setting-card">
                      <h3>⏳ Haber Verisi Süre Sınırı</h3>
                      <select value={timeLimit} onChange={(e) => setTimeLimit(e.target.value)} style={{marginBottom: timeLimit === 'custom' ? '1rem' : '0'}}>
                        <option value="1_month">Katı Kalkan: Yalnızca Son 1 Ay</option><option value="2_months">Standart Kalkan: Son 2 Ay (Önerilen)</option><option value="unlimited">Kalkanı Kapat: Tüm Zamanlar</option><option value="custom">ÖZEL SINIR BELİRLE (Gün Sayısı Girin)</option>
                      </select>
                      {timeLimit === 'custom' && (
                        <div style={{display: 'flex', alignItems: 'center', gap: '1rem', background: 'rgba(0,0,0,0.2)', padding: '1rem', borderRadius: '10px', border: '1px solid var(--accent-color)'}}>
                          <span style={{fontSize: '0.9rem'}}>Yalnızca Son</span>
                          <input type="number" min="1" value={customDays} onChange={(e) => setCustomDays(parseInt(e.target.value) || 1)} style={{width: '90px', padding: '0.5rem', background: 'rgba(255,255,255,0.1)'}} />
                          <span style={{fontSize: '0.9rem'}}>günlük haberleri getir.</span>
                        </div>
                      )}
                    </div>
                    <div className="setting-card">
                      <h3>🧠 Yaratıcılık Seviyesi (Temperature)</h3>
                      <input type="range" min="0" max="1" step="0.1" value={temperature} onChange={(e) => setTemperature(parseFloat(e.target.value))} />
                    </div>
                    <div className="card-grid" style={{gridTemplateColumns: '1fr 1fr', gap: '1rem'}}>
                      <div className="setting-card" style={{height: '100%', marginBottom: 0}}>
                        <h3>📝 Cevap Uzunluğu</h3>
                        <select value={maxTokens} onChange={(e) => setMaxTokens(e.target.value)}><option value="short">Kısa</option><option value="medium">Orta</option><option value="long">Uzun</option></select>
                      </div>
                      <div className="setting-card" style={{height: '100%', marginBottom: 0}}>
                        <h3>📁 Kaynak Önceliği</h3>
                        <select value={sourceFilter} onChange={(e) => setSourceFilter(e.target.value)}><option value="all">Tümü (Karma)</option><option value="news_only">Sadece Haberler</option><option value="corp_only">Sadece Kurumsal</option></select>
                      </div>
                    </div>
                  </div>
                )}

                {/* 2. GÖRÜNÜM VE ARAYÜZ */}
                {activeSettingsCategory === 'appearance' && (
                  <div className="card-grid" style={{gridTemplateColumns: '1fr 1fr', gap: '1.5rem'}}>
                    <div style={{gridColumn: '1 / -1'}}><h2 className="settings-section-title">Arayüz ve Marka Özelleştirmesi</h2></div>
                    <div className="setting-card" style={{gridColumn: '1 / -1'}}>
                      <h3>🎨 Kurumsal Vurgu Rengi</h3>
                      <div style={{display: 'flex', gap: '1rem', flexWrap: 'wrap', marginTop: '1rem'}}>
                        <div className={`color-circle ${accentColor === '#3b82f6' ? 'active' : ''}`} style={{backgroundColor: '#3b82f6'}} onClick={() => setAccentColor('#3b82f6')}></div><div className={`color-circle ${accentColor === '#8b5cf6' ? 'active' : ''}`} style={{backgroundColor: '#8b5cf6'}} onClick={() => setAccentColor('#8b5cf6')}></div><div className={`color-circle ${accentColor === '#10b981' ? 'active' : ''}`} style={{backgroundColor: '#10b981'}} onClick={() => setAccentColor('#10b981')}></div><div className={`color-circle ${accentColor === '#ef4444' ? 'active' : ''}`} style={{backgroundColor: '#ef4444'}} onClick={() => setAccentColor('#ef4444')}></div><div className={`color-circle ${accentColor === '#f59e0b' ? 'active' : ''}`} style={{backgroundColor: '#f59e0b'}} onClick={() => setAccentColor('#f59e0b')}></div><div className={`color-circle ${accentColor === '#ec4899' ? 'active' : ''}`} style={{backgroundColor: '#ec4899'}} onClick={() => setAccentColor('#ec4899')}></div><div className={`color-circle ${accentColor === '#14b8a6' ? 'active' : ''}`} style={{backgroundColor: '#14b8a6'}} onClick={() => setAccentColor('#14b8a6')}></div><div className={`color-circle ${accentColor === '#64748b' ? 'active' : ''}`} style={{backgroundColor: '#64748b'}} onClick={() => setAccentColor('#64748b')}></div><div className={`color-circle ${accentColor === '#0B3D62' ? 'active' : ''}`} style={{backgroundColor: '#0B3D62'}} onClick={() => setAccentColor('#0B3D62')}></div>
                      </div>
                    </div>
                    <div className="setting-card" style={{gridColumn: '1 / -1'}}><h3 style={{marginBottom: '0.5rem'}}>🏷️ Chatbot (Asistan) Adı</h3><input type="text" value={aiName} onChange={(e) => setAiName(e.target.value)} /></div>
                    <div className="setting-card" style={{gridColumn: '1 / -1'}}><h3 style={{marginBottom: '0.5rem'}}>👋 Karşılama Alt Metni</h3><input type="text" value={greetingText} onChange={(e) => setGreetingText(e.target.value)} /></div>
                    <div className="setting-card" style={{gridColumn: '1 / -1'}}><h3 style={{marginBottom: '0.5rem'}}>💬 Arama Kutusu İpucu (Placeholder)</h3><input type="text" value={inputPlaceholder} onChange={(e) => setInputPlaceholder(e.target.value)} /></div>
                    <div className="setting-card" style={{gridColumn: '1 / -1'}}><h3 style={{marginBottom: '0.5rem'}}>💡 Örnek Sorular (Lütfen virgülle ayırın)</h3><input type="text" value={suggestedPrompts} onChange={(e) => setSuggestedPrompts(e.target.value)} /></div>
                    <div className="setting-card"><h3>👤 Kullanıcı Hitap Şekli (Lakap)</h3><input type="text" value={userNickname} onChange={(e) => setUserNickname(e.target.value)} style={{marginTop: '0.5rem'}} /></div>
                    <div className="setting-card"><h3>🌓 Tema Modu</h3><select value={themeMode} onChange={(e) => setThemeMode(e.target.value)} style={{marginTop: '0.5rem'}}><option value="dark">Gece Modu</option><option value="light">Gündüz Modu</option></select></div>
                    <div className="setting-card"><h3>🔤 Yazı Boyutu</h3><select value={fontSize} onChange={(e) => setFontSize(e.target.value)} style={{marginTop: '0.5rem'}}><option value="small">Küçük</option><option value="medium">Orta</option><option value="large">Büyük</option></select></div>
                    <div className="setting-card"><h3>📏 Sohbet Genişliği</h3><select value={chatWidth} onChange={(e) => setChatWidth(e.target.value)} style={{marginTop: '0.5rem'}}><option value="narrow">Dar</option><option value="standard">Standart</option><option value="wide">Geniş</option></select></div>
                  </div>
                )}
                
                {/* 3. GÜVENLİK VE API AYARLARI (YENİ SİSTEMLER) */}
                {activeSettingsCategory === 'security' && (
                  <div className="card-grid" style={{gridTemplateColumns: '1fr 1fr', gap: '1.5rem'}}>
                    <div style={{gridColumn: '1 / -1'}}>
                      <h2 className="settings-section-title">Güvenlik ve Kurumsal API Yönetimi</h2>
                    </div>

                    {/* ACİL KAPATMA (KILL SWITCH) */}
                    <div className="setting-card" style={{gridColumn: '1 / -1', border: killSwitch ? '2px solid #ef4444' : '1px solid rgba(255,255,255,0.05)', backgroundColor: killSwitch ? 'rgba(239, 68, 68, 0.1)' : 'rgba(0,0,0,0.2)'}}>
                      <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center'}}>
                        <div>
                          <h3 style={{marginBottom: '0.5rem', color: killSwitch ? '#ef4444' : 'inherit'}}>🚨 Acil Durum Kapatma (Kill Switch)</h3>
                          <p style={{color: 'var(--text-secondary)', fontSize: '0.9rem', maxWidth: '80%'}}>Olası bir siber saldırı veya bütçe aşımında Chatbot'un LLM motorunu tamamen durdurarak maliyetleri korur.</p>
                        </div>
                        <button 
                          onClick={() => setKillSwitch(!killSwitch)}
                          style={{
                            padding: '0.8rem 1.5rem', borderRadius: '8px', fontWeight: 'bold', border: 'none', cursor: 'pointer',
                            backgroundColor: killSwitch ? '#ef4444' : 'rgba(255,255,255,0.1)', color: 'white', transition: 'all 0.3s', whiteSpace: 'nowrap'
                          }}>
                          {killSwitch ? "SİSTEM DURDURULDU (Aç)" : "Sistemi Durdur (Kill Switch)"}
                        </button>
                      </div>
                    </div>

                    {/* API ANAHTARI */}
                    <div className="setting-card" style={{gridColumn: '1 / -1'}}>
                      <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '1rem'}}>
                        <div><h3 style={{marginBottom: '0.5rem'}}>🔑 OpenAI / LLM API Key</h3><p style={{color: 'var(--text-secondary)', fontSize: '0.9rem'}}>Yapay zeka modelinin yetki anahtarı.</p></div>
                      </div>
                      <div style={{background: 'rgba(0,0,0,0.3)', padding: '1rem', borderRadius: '10px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', border: '1px solid rgba(255,255,255,0.05)'}}>
                        <div style={{display: 'flex', alignItems: 'center', gap: '1rem'}}>
                          <span style={{fontSize: '1.5rem'}}>🔐</span>
                          <div>
                            {isEditingApi ? (
                               <input type="text" autoFocus placeholder="sk-..." value={apiKey} onChange={(e) => setApiKey(e.target.value)} style={{ width: '250px', padding: '0.4rem 0.8rem', borderRadius: '6px', background: 'rgba(255,255,255,0.1)', border: '1px solid var(--accent-color)', color: 'white', outline: 'none' }} />
                            ) : (
                               <div style={{fontFamily: 'monospace', letterSpacing: '2px', color: '#e2e8f0'}}>{apiKey ? `sk-****...${apiKey.slice(-4)}` : 'sk-***********************'}</div>
                            )}
                          </div>
                        </div>
                        <button className="btn-primary" style={{padding: '0.5rem 1rem', fontSize: '0.85rem', backgroundColor: isEditingApi ? 'var(--accent-color)' : 'transparent', border: '1px solid var(--accent-color)', color: isEditingApi ? 'white' : 'var(--accent-color)'}} onClick={() => setIsEditingApi(!isEditingApi)}>
                          {isEditingApi ? "Sakla" : "Anahtarı Değiştir"}
                        </button>
                      </div>
                    </div>

                    {/* FİLTRELER VE MASKELER */}
                    <div className="setting-card">
                      <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem'}}>
                        <h3>🤬 Küfür ve Zararlı İçerik Filtresi</h3>
                        <input type="checkbox" checked={profanityFilter} onChange={(e) => setProfanityFilter(e.target.checked)} style={{width: '20px', height: '20px', cursor: 'pointer'}} />
                      </div>
                      <p style={{color: 'var(--text-secondary)', fontSize: '0.85rem'}}>Uygunsuz veya prompt-injection saldırısı içeren soruları LLM'e gitmeden API aşamasında bloklar.</p>
                    </div>

                    <div className="setting-card">
                      <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem'}}>
                        <h3>🕵️ Hassas Veri Maskeleme (PII)</h3>
                        <input type="checkbox" checked={piiMasking} onChange={(e) => setPiiMasking(e.target.checked)} style={{width: '20px', height: '20px', cursor: 'pointer'}} />
                      </div>
                      <p style={{color: 'var(--text-secondary)', fontSize: '0.85rem'}}>Kullanıcı sorusundaki T.C. Kimlik, Telefon vb. verileri sunucuya göndermeden önce `***` ile gizler.</p>
                    </div>

                    {/* KOTA VE UZUNLUK */}
                    <div className="setting-card">
                      <h3>📏 Maks. Soru Uzunluğu (Karakter)</h3>
                      <p style={{color: 'var(--text-secondary)', fontSize: '0.85rem', marginBottom: '1rem'}}>Spam engellemek için bir kullanıcının yazabileceği en uzun metin limiti.</p>
                      <div style={{display: 'flex', alignItems: 'center', gap: '1rem'}}>
                        <input type="range" min="100" max="2000" step="100" value={maxPromptLength} onChange={(e) => setMaxPromptLength(Number(e.target.value))} style={{flex: 1}} />
                        <span style={{fontWeight: 'bold', width: '40px'}}>{maxPromptLength}</span>
                      </div>
                    </div>

                    <div className="setting-card">
                      <h3>⏱️ İstek Kotası (Rate Limit)</h3>
                      <p style={{color: 'var(--text-secondary)', fontSize: '0.85rem', marginBottom: '1rem'}}>Aynı kullanıcının (IP adresinin) günlük soru sorma hakkı sınırı.</p>
                      <div style={{display: 'flex', alignItems: 'center', gap: '0.5rem'}}>
                        <input type="number" min="1" max="1000" value={rateLimit} onChange={(e) => setRateLimit(Number(e.target.value))} style={{width: '80px', padding: '0.5rem', background: 'rgba(255,255,255,0.1)', border: '1px solid rgba(255,255,255,0.2)', color: 'white', borderRadius: '5px'}} />
                        <span style={{fontSize: '0.9rem', color: 'var(--text-secondary)'}}>soru / gün</span>
                      </div>
                    </div>

                    {/* CORS WHITELIST */}
                    <div className="setting-card" style={{gridColumn: '1 / -1'}}>
                      <h3>🌍 İzinli Alan Adları (CORS / Whitelist)</h3>
                      <p style={{color: 'var(--text-secondary)', fontSize: '0.85rem', marginBottom: '0.5rem'}}>API sunucunuza (Chatbot'a) sadece aşağıdaki domainlerden gelen istekler kabul edilir (Virgülle ayırın).</p>
                      <input type="text" value={allowedDomains} onChange={(e) => setAllowedDomains(e.target.value)} placeholder="Örn: localhost, konya.bel.tr, koski.gov.tr" />
                    </div>

                  </div>
                )}
              </div>
            </div>

            <div style={{display: 'flex', justifyContent: 'flex-end', padding: '1rem', background: 'rgba(0,0,0,0.2)', borderTop: '1px solid rgba(255,255,255,0.05)', borderBottomRightRadius: '15px', borderBottomLeftRadius: '15px'}}>
              <button 
                onClick={handleSave} 
                disabled={isSaving}
                style={{
                  backgroundColor: 'var(--accent-color)', color: 'white', padding: '0.75rem 2rem', 
                  borderRadius: '10px', fontSize: '1rem', fontWeight: 'bold', border: 'none', cursor: 'pointer',
                  opacity: isSaving ? 0.7 : 1, transition: 'all 0.3s'
                }}
              >
                {isSaving ? '⏳ Kaydediliyor...' : '💾 Tüm Ayarları Kaydet'}
              </button>
            </div>
          </div>
        )}
      </main>
    </div>
  );
};

export default App;