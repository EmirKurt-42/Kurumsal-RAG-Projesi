"use client";

import { useState, useEffect, useRef } from "react";

const API_URL = "http://127.0.0.1:8000";

function formatMarkdown(text, kaynaklar = [], accentColor = "#0B3D62") {
  if (!text) return "";
  let parsed = text;
  
  parsed = parsed.replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>");
  parsed = parsed.replace(/\[([^\]]+)\]\(([^)]+)\)/g, `<a href="$2" target="_blank" style="color: ${accentColor}; text-decoration: underline; font-weight: 500;">$1</a>`);
  
  if (kaynaklar && kaynaklar.length > 0) {
    const regex = /(?:\[|\()(?:Kaynak\s*|Source\s*)?(\d+)(?:\]|\))/gi;
    parsed = parsed.replace(regex, (match, numStr) => {
      const idx = parseInt(numStr, 10) - 1;
      if (idx >= 0 && idx < kaynaklar.length) {
        const kaynakObj = kaynaklar[idx];
        const url = kaynakObj.url;
        
        if (url && url !== "#") {
          return `<a href="${url}" target="_blank" style="color: ${accentColor}; font-size: 0.85em; text-decoration: none; font-weight: 700; padding: 2px 6px; border-radius: 6px; background-color: ${accentColor}1A; border: 1px solid ${accentColor}33; vertical-align: middle; margin: 0 2px; transition: all 0.2s;" onMouseOver="this.style.backgroundColor='${accentColor}33'" onMouseOut="this.style.backgroundColor='${accentColor}1A'" title="${kaynakObj.baslik}">[Kaynak ${numStr}]</a>`;
        } else {
          return `<span style="color: ${accentColor}; font-size: 0.85em; font-weight: 700; padding: 2px 6px; border-radius: 6px; background-color: ${accentColor}1A; border: 1px solid ${accentColor}33; vertical-align: middle; margin: 0 2px;" title="${kaynakObj.baslik}">[Kaynak ${numStr}]</span>`;
        }
      }
      return match; 
    });
  }

  const lines = parsed.split('\n');
  let htmlOutput = "";
  let inList = false;
  lines.forEach((line) => {
    const trimmed = line.trim();
    if (trimmed.startsWith("- ") || trimmed.startsWith("* ")) {
      if (!inList) { htmlOutput += '<ul class="list-disc pl-5 my-2 space-y-1">'; inList = true; }
      htmlOutput += `<li class="leading-relaxed">${trimmed.substring(2)}</li>`;
    } else {
      if (inList) { htmlOutput += '</ul>'; inList = false; }
      if (trimmed !== "") htmlOutput += `<p class="whitespace-pre-wrap mb-2 last:mb-0 leading-relaxed">${line}</p>`;
    }
  });
  if (inList) htmlOutput += '</ul>';
  return htmlOutput;
}

function stringToColor(str) {
  if (!str) return { bg: "#94a3b8", text: "#ffffff" }; 
  const lowerStr = str.toLowerCase();
  if (lowerStr.includes("koski")) return { bg: "#2563EB", text: "#ffffff" }; 
  if (lowerStr.includes("konyakart")) return { bg: "#16A34A", text: "#ffffff" }; 
  if (lowerStr.includes("komek")) return { bg: "#EAB308", text: "#ffffff" }; 
  if (lowerStr.includes("haber") || lowerStr.includes("bulten")) return { bg: "#ffffff", text: "#0B3D62" }; 
  let hash = 0;
  for (let i = 0; i < str.length; i++) hash = str.charCodeAt(i) + ((hash << 5) - hash);
  const h = Math.abs(hash) % 360;
  return { bg: `hsl(${h}, 65%, 45%)`, text: "#ffffff" };
}

function TypingDots({ color }) {
  return (
    <div className="flex items-center gap-1.5 px-1 py-1.5">
      {[0, 1, 2].map((i) => (
        <span key={i} className="h-2 w-2 animate-bounce rounded-full" style={{ backgroundColor: color, animationDelay: `${i * 0.15}s` }} />
      ))}
    </div>
  );
}

export default function Home() {
  const [soru, setSoru] = useState("");
  const [gecmis, setGecmis] = useState([]);
  const [yukleniyor, setYukleniyor] = useState(false);
  const [hata, setHata] = useState(null);
  
  const [sessionId, setSessionId] = useState(null);
  const [acikKaynaklar, setAcikKaynaklar] = useState({});
  const mesajlarSonuRef = useRef(null);

  const [settings, setSettings] = useState({
    accentColor: "#0B3D62",
    themeMode: "dark",
    fontSize: "medium",
    chatWidth: "standard",
    aiName: "Konya Veri Asistanı",
    userNickname: "Sen",
    greetingText: "Kurumsal RAG Demosu",
    inputPlaceholder: "Sorunuzu yazın...",
    suggestedPrompts: "KOSKİ su faturası nasıl ödenir?, Komek hangi eğitimleri veriyor?, Konya'da son haberler neler?",
    killSwitch: false,
    maxPromptLength: 500
  });

  useEffect(() => {
    const fetchSettings = async () => {
      try {
        const res = await fetch(`${API_URL}/admin/settings`);
        if(res.ok) {
          const data = await res.json();
          setSettings(prev => ({...prev, ...data}));
        }
      } catch (e) {}
    };
    fetchSettings();
    const interval = setInterval(fetchSettings, 1500);
    return () => clearInterval(interval);
  }, []);

  const asagiKaydir = () => mesajlarSonuRef.current?.scrollIntoView({ behavior: "smooth" });
  useEffect(() => { asagiKaydir(); }, [gecmis, yukleniyor]);

  function toggleKaynaklar(index) { setAcikKaynaklar(prev => ({ ...prev, [index]: !prev[index] })); }

  // YENİ: Gece Yarısı / Ertesi Gün Sohbet Sıfırlama Mantığı
  useEffect(() => {
    // "2026-08-10" formatında sadece bugünün tarihini al
    const today = new Date().toISOString().split('T')[0];
    const savedDate = sessionStorage.getItem("chat_date");

    // Eğer eski bir tarih kayıtlıysa (veya hiç tarih yoksa), eski sohbeti imha et
    if (savedDate !== today) {
      sessionStorage.removeItem("aktif_session_id");
      sessionStorage.setItem("chat_date", today);
    } else {
      // Hala aynı gündeysek, mevcut sohbeti ekrana yükle
      const sonSessionId = sessionStorage.getItem("aktif_session_id");
      if (sonSessionId) sohbetiYukle(sonSessionId);
    }
  }, []);

  async function sohbetiYukle(id) {
    setYukleniyor(true); setHata(null);
    try {
      const res = await fetch(`${API_URL}/sessions/${id}`);
      if (res.ok) {
        const data = await res.json();
        setGecmis(data.history); 
        setSessionId(id);
      }
    } catch (e) { setHata("Sohbet yüklenemedi."); } 
    finally { setYukleniyor(false); }
  }

  async function soruyuGonder(gonderilecekSoru) {
    if (!gonderilecekSoru || yukleniyor || settings.killSwitch) return;
    setSoru(""); setHata(null); setYukleniyor(true);
    setGecmis((onceki) => [...onceki, { rol: "kullanici", metin: gonderilecekSoru }]);
    try {
      const res = await fetch(`${API_URL}/ask`, {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ soru: gonderilecekSoru, session_id: sessionId }),
      });
      if (res.status === 429) throw new Error(`Çok fazla istek attınız (Kota aşıldı). Lütfen bekleyin.`);
      if (!res.ok) throw new Error(`Sunucu hatası`);
      
      const veri = await res.json();
      setGecmis((onceki) => [ ...onceki, { rol: "asistan", metin: veri.cevap, kaynaklar: veri.kaynaklar } ]);
      
      if (!sessionId) {
        setSessionId(veri.session_id); 
        sessionStorage.setItem("aktif_session_id", veri.session_id);
      }
    } catch (err) { setHata(err.message || "Sunucuya ulaşılamadı."); } 
    finally { setYukleniyor(false); }
  }

  function handleSubmit(e) { e.preventDefault(); soruyuGonder(soru.trim()); }

  const isDark = settings.themeMode === 'dark';
  const rootBg = isDark ? "bg-[#0A1A26]" : "bg-[#F2F6F9]";
  const rootText = isDark ? "text-white" : "text-gray-900";
  const chatAreaBg = isDark ? "bg-[#112233]" : "bg-white";
  const aiBubbleBg = isDark ? "bg-[#1A2F45]" : "bg-[#F2F6F9]";
  const widthClass = settings.chatWidth === 'narrow' ? 'max-w-xl' : settings.chatWidth === 'wide' ? 'max-w-4xl' : 'max-w-2xl';
  const textSize = settings.fontSize === 'small' ? 'text-xs' : settings.fontSize === 'large' ? 'text-base' : 'text-sm';
  const ornekler = settings.suggestedPrompts ? settings.suggestedPrompts.split(',').filter(s => s.trim() !== '') : [];

  return (
    <div className={`flex h-screen overflow-hidden ${rootBg} ${rootText} transition-colors duration-500`}>
      {/* SOLDAKİ SOHBET GEÇMİŞİ PANELİ TAMAMEN SİLİNDİ */}

      {/* SOHBET EKRANI (TAM EKRAN VE MERKEZLİ) */}
      <div className="flex-1 flex flex-col h-full relative overflow-y-auto w-full">
        <div className={`flex flex-col items-center px-4 py-8 h-full w-full ${widthClass} mx-auto transition-all duration-500`}>
          
          <header className="w-full relative overflow-hidden rounded-2xl px-6 py-6 text-white mb-5 shadow-md transition-colors duration-500" style={{ backgroundColor: settings.accentColor }}>
            <div className="pointer-events-none absolute -right-10 -top-16 h-40 w-40 rounded-full bg-black/20" />
            <p className="relative text-[11px] font-semibold tracking-widest text-white/80">YAPAY ZEKA MERKEZİ</p>
            <h1 className="relative mt-1 text-2xl font-bold">{settings.aiName}</h1>
            <p className="relative mt-1 text-sm text-white/90">{settings.greetingText}</p>
          </header>

          <div className={`w-full flex-1 flex flex-col gap-4 rounded-2xl border ${isDark ? 'border-gray-800' : 'border-[#E1E9EF]'} ${chatAreaBg} p-4 shadow-sm overflow-y-auto mb-5 scroll-smooth transition-colors duration-500`}>
            {gecmis.length === 0 && (
              <div className="m-auto flex flex-col items-center gap-4 py-6 text-center">
                <p className={`text-sm ${isDark ? 'text-gray-400' : 'text-gray-500'}`}>Örneklerden birini deneyin:</p>
                <div className="flex flex-wrap justify-center gap-2">
                  {ornekler.map((s, idx) => (
                    <button key={idx} disabled={settings.killSwitch} onClick={() => soruyuGonder(s)} className={`rounded-full border px-3 py-1.5 ${textSize} font-medium ${isDark ? 'bg-transparent hover:bg-white/5' : 'bg-gray-50 hover:bg-gray-100'} transition-colors disabled:opacity-50 disabled:cursor-not-allowed`} style={{ color: settings.accentColor, borderColor: settings.accentColor }}>
                      {s.trim()}
                    </button>
                  ))}
                </div>
              </div>
            )}

            {gecmis.map((mesaj, i) => (
              <div key={i} className={`flex items-start gap-2.5 ${mesaj.rol === "kullanici" ? "flex-row-reverse" : "flex-row"}`}>
                <div className={`flex h-8 w-8 shrink-0 items-center justify-center rounded-full text-xs font-semibold text-white transition-colors duration-500`} style={{ backgroundColor: settings.accentColor }}>
                  {mesaj.rol === "kullanici" ? settings.userNickname : "AI"}
                </div>
                <div className={`max-w-[80%] rounded-2xl px-4 py-3 shadow-sm transition-colors duration-500 ${mesaj.rol === "kullanici" ? "rounded-tr-sm text-white" : `rounded-tl-sm ${aiBubbleBg} ${isDark ? 'text-white' : 'text-[#1A2733]'}`}`} style={mesaj.rol === "kullanici" ? { backgroundColor: settings.accentColor } : {}}>
                  <div className={`${textSize} leading-relaxed`} dangerouslySetInnerHTML={{ __html: formatMarkdown(mesaj.metin, mesaj.kaynaklar, settings.accentColor) }} />
                  {mesaj.kaynaklar && mesaj.kaynaklar.length > 0 && (
                    <div className="mt-3 border-t border-black/10 pt-2.5">
                      <button onClick={() => toggleKaynaklar(i)} className="text-xs font-medium hover:underline" style={{ color: settings.accentColor }}>
                        {acikKaynaklar[i] ? "Kaynakları Gizle" : `${mesaj.kaynaklar.length} Kaynağı Göster`}
                      </button>
                      {acikKaynaklar[i] && (
                        <div className="flex flex-col gap-2 mt-2">
                          {mesaj.kaynaklar.map((k, j) => {
                            const renk = stringToColor(k.kaynak);
                            return (
                              <div key={j} className="flex items-start gap-2.5 rounded-lg border bg-black/5 p-2 shadow-sm dark:border-gray-700">
                                <div style={{ backgroundColor: renk.bg, color: renk.text }} className="flex h-5 w-5 shrink-0 items-center justify-center rounded-full text-[9px] font-bold">{k.kaynak.charAt(0).toUpperCase()}</div>
                                <div className="flex flex-col">
                                  <span className="text-[11px] font-bold uppercase" style={{ color: settings.accentColor }}>{k.kaynak}</span>
                                  <a href={k.url || "#"} target="_blank" className={`text-xs ${isDark ? 'text-gray-300' : 'text-gray-500'} hover:underline`}>{k.baslik}</a>
                                </div>
                              </div>
                            );
                          })}
                        </div>
                      )}
                    </div>
                  )}
                </div>
              </div>
            ))}

            {yukleniyor && (
              <div className="flex items-start gap-2.5">
                <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full text-white transition-colors duration-500" style={{ backgroundColor: settings.accentColor }}>AI</div>
                <div className={`rounded-2xl rounded-tl-sm ${aiBubbleBg} px-2 py-1 shadow-sm`}><TypingDots color={settings.accentColor} /></div>
              </div>
            )}
            {hata && <p className="rounded-lg bg-red-50 dark:bg-red-900/30 px-3 py-2 text-sm text-red-700 dark:text-red-400">{hata}</p>}
            <div ref={mesajlarSonuRef} />
          </div>

          <form onSubmit={handleSubmit} className="w-full flex flex-col gap-1">
            <div className="w-full flex gap-2">
              <input 
                type="text" 
                value={soru} 
                onChange={(e) => setSoru(e.target.value)} 
                maxLength={settings.maxPromptLength}
                placeholder={settings.killSwitch ? "🚨 Sistem şu an bakımdadır, lütfen daha sonra tekrar deneyin." : settings.inputPlaceholder} 
                disabled={yukleniyor || settings.killSwitch}
                className={`flex-1 rounded-full border px-5 py-4 ${textSize} outline-none transition-all duration-500 ${isDark ? 'bg-[#112233] border-gray-700 text-white' : 'bg-white text-gray-900'} ${(yukleniyor || settings.killSwitch) ? 'opacity-50 cursor-not-allowed' : ''}`} 
                style={{ borderColor: settings.killSwitch ? '#ef4444' : settings.accentColor }} 
              />
              <button 
                type="submit" 
                disabled={yukleniyor || settings.killSwitch || !soru.trim()} 
                className={`flex items-center justify-center gap-1.5 rounded-full px-6 py-4 ${textSize} font-semibold text-white shadow-md transition-all duration-500 hover:opacity-90 hover:scale-105 disabled:opacity-50 disabled:hover:scale-100 disabled:cursor-not-allowed`} 
                style={{ backgroundColor: settings.killSwitch ? '#ef4444' : settings.accentColor }}>
                Gönder
              </button>
            </div>
            {!settings.killSwitch && (
              <div className={`text-right px-4 text-[10px] mt-1 transition-colors duration-300 ${soru.length >= settings.maxPromptLength ? 'text-red-500 font-bold' : 'text-gray-400'}`}>
                {soru.length} / {settings.maxPromptLength} karakter
              </div>
            )}
          </form>
        </div>
      </div>
    </div>
  );
}