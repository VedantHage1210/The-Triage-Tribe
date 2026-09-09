import { useEffect, useRef, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { useLanguage } from "../context/LanguageContext";
import { submitTriage, submitVisualCheck } from "../services/triageService";
import Header from "../components/Header";
import Footer from "../components/Footer";
import DisclaimerBanner from "../components/DisclaimerBanner";
import TriageResultCard from "../components/TriageResultCard";
import ObservationCard from "../components/ObservationCard";

const IMAGE_CATEGORIES = ["eyes", "skin"]; // Section 10.1 scope
const QUICK_PROMPTS = {
  eyes: ["redness", "itching", "pain", "blurred vision"],
  skin: ["rash", "itching", "swelling", "fever"],
  heart: ["chest discomfort", "shortness of breath", "dizziness", "palpitations"],
  digestion: ["nausea", "vomiting", "diarrhea", "abdominal pain"],
  general: ["fever", "fatigue", "pain", "started suddenly"],
};

export default function TriagePage() {
  const { category } = useParams();
  const { t } = useTranslation();
  const { language } = useLanguage();
  const navigate = useNavigate();

  const [text, setText] = useState("");
  const [patientInfo, setPatientInfo] = useState({ name: "", age: "", bloodGroup: "" });
  const [showPatientInfo, setShowPatientInfo] = useState(false);
  const [loading, setLoading] = useState(false);
  const [sessionId, setSessionId] = useState(null);
  const [followUpQuestions, setFollowUpQuestions] = useState([]);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [imageFile, setImageFile] = useState(null);
  const [observation, setObservation] = useState(null);
  const [uploadingImage, setUploadingImage] = useState(false);
  const [isListening, setIsListening] = useState(false);
  const [voiceError, setVoiceError] = useState("");
  const recognitionRef = useRef(null);

  const supportsImage = IMAGE_CATEGORIES.includes(category);
  const quickPrompts = QUICK_PROMPTS[category] || QUICK_PROMPTS.general;
  const snapshotProgress = Math.min(
    100,
    Math.round((text.trim().length > 20 ? 50 : text.trim() ? 25 : 0) +
      (/\b(day|days|week|weeks|hour|hours|since|today|gestern|tage|woche)\b/i.test(text) ? 25 : 0) +
      (/\b(mild|moderate|severe|worst|mild|stark|leicht|schlimm)\b/i.test(text) ? 25 : 0))
  );

  useEffect(() => {
    const draft = localStorage.getItem(`triage_draft_${category}_${language}`);
    if (draft && !text) setText(draft);
  }, [category, language]);

  useEffect(() => {
    if (text) localStorage.setItem(`triage_draft_${category}_${language}`, text);
  }, [text, category, language]);

  useEffect(() => () => recognitionRef.current?.stop(), []);

  const addPrompt = (prompt) => {
    setText((current) => (current.trim() ? `${current.trim()} ${prompt}.` : `${prompt}.`));
  };

  const toggleVoiceInput = () => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      setVoiceError(t("triage.voiceUnsupported"));
      return;
    }
    if (isListening) {
      recognitionRef.current?.stop();
      return;
    }
    const recognition = new SpeechRecognition();
    recognition.lang = language === "de" ? "de-DE" : "en-US";
    recognition.interimResults = false;
    recognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript;
      setText((current) => (current.trim() ? `${current.trim()} ${transcript}` : transcript));
    };
    recognition.onerror = () => setVoiceError(t("triage.voiceUnsupported"));
    recognition.onend = () => setIsListening(false);
    recognitionRef.current = recognition;
    setVoiceError("");
    setIsListening(true);
    recognition.start();
  };

  const handleImageUpload = async (file) => {
    if (!file || !result?.session_id) return;
    setImageFile(file);
    setUploadingImage(true);
    try {
      const obs = await submitVisualCheck({
        sessionId: result.session_id,
        category,
        language,
        file,
      });
      setObservation(obs);
    } catch (err) {
      // Fails gracefully — the text-based triage result already stands
      // on its own; the image observation is an additive enhancement.
      setObservation(null);
    } finally {
      setUploadingImage(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!text.trim()) return;

    setLoading(true);
    setError(null);
    try {
      const data = await submitTriage({
        text,
        language,
        category,
        sessionId,
        patientInfo,
      });

      setSessionId(data.session_id);
      localStorage.removeItem(`triage_draft_${category}_${language}`);

      if (data.needs_follow_up) {
        // Section 7.4 — adaptive multi-turn loop: show the AI's own
        // follow-up question(s) instead of a final result.
        setFollowUpQuestions(data.follow_up_questions);
        setResult(null);
        setText("");
      } else {
        setFollowUpQuestions([]);
        setResult(data);
      }
    } catch (err) {
      setError(t("common.loading"));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex flex-col bg-bg-soft">
      <DisclaimerBanner />
      <Header />

      <div className="px-6 pt-4">
        <button
          onClick={() => navigate("/")}
          className="text-sm text-slate-500 hover:text-ink"
        >
          ← {t("common.back")}
        </button>
      </div>

      <main className="flex-1 flex flex-col items-center px-6 py-8">
        {!result && (
          <div className="w-full max-w-md">
            {followUpQuestions.length > 0 && (
              <div className="bg-clinical-teal/10 border border-clinical-teal/30 rounded-xl p-4 mb-4">
                <p className="text-sm text-slate-600 mb-2">{t("triage.answerFollowUp")}</p>
                {followUpQuestions.map((q, i) => (
                  <p key={i} className="text-ink font-medium mb-1">
                    {q}
                  </p>
                ))}
              </div>
            )}

            <div className="w-full max-w-md mb-4">
              <div className="flex items-end justify-between mb-2">
                <div>
                  <p className="text-lg font-semibold text-ink">{t("triage.snapshotTitle")}</p>
                  <p className="text-xs text-slate-500 mt-1">{t("triage.snapshotSubtitle")}</p>
                </div>
                <span className="text-xs font-medium text-clinical-teal">{snapshotProgress}%</span>
              </div>
              <div className="h-1.5 bg-slate-200 rounded-full overflow-hidden">
                <div className="h-full bg-clinical-teal rounded-full transition-all" style={{ width: `${snapshotProgress}%` }} />
              </div>
            </div>

            <form onSubmit={handleSubmit} className="flex flex-col gap-3">
              <div className="flex flex-wrap gap-2">
                <span className="text-xs text-slate-500 w-full">{t("triage.quickPrompts")}</span>
                {quickPrompts.map((prompt) => (
                  <button key={prompt} type="button" onClick={() => addPrompt(prompt)}
                    className="rounded-full border border-clinical-teal/30 bg-clinical-teal/5 px-3 py-1.5 text-xs text-clinical-teal hover:bg-clinical-teal/10">
                    + {prompt}
                  </button>
                ))}
              </div>
              <textarea
                value={text}
                onChange={(e) => setText(e.target.value)}
                placeholder={t("triage.inputPlaceholder")}
                rows={5}
                className="w-full rounded-xl border border-slate-200 p-4 text-ink focus:outline-none focus:ring-2 focus:ring-clinical-teal resize-none"
              />
              <div className="flex items-center justify-between">
                <button type="button" onClick={toggleVoiceInput}
                  className={`text-sm ${isListening ? "text-severity-emergency" : "text-clinical-teal"}`}>
                  {isListening ? "● " : "🎙 "} {isListening ? t("triage.voiceListening") : t("triage.voiceInput")}
                </button>
                <span className="text-xs text-slate-400">{t("triage.privacyNote")}</span>
              </div>
              {voiceError && <p className="text-xs text-severity-urgent">{voiceError}</p>}

              {!showPatientInfo && !sessionId && (
                <button
                  type="button"
                  onClick={() => setShowPatientInfo(true)}
                  className="text-sm text-clinical-teal self-start"
                >
                  + {t("triage.patientInfoTitle")}
                </button>
              )}

              {showPatientInfo && (
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-2">
                  <input
                    type="text"
                    placeholder={t("triage.name")}
                    value={patientInfo.name}
                    onChange={(e) => setPatientInfo({ ...patientInfo, name: e.target.value })}
                    className="rounded-lg border border-slate-200 p-2 text-sm"
                  />
                  <input
                    type="number"
                    placeholder={t("triage.age")}
                    value={patientInfo.age}
                    onChange={(e) => setPatientInfo({ ...patientInfo, age: e.target.value })}
                    className="rounded-lg border border-slate-200 p-2 text-sm"
                  />
                  <input
                    type="text"
                    placeholder={t("triage.bloodGroup")}
                    value={patientInfo.bloodGroup}
                    onChange={(e) => setPatientInfo({ ...patientInfo, bloodGroup: e.target.value })}
                    className="rounded-lg border border-slate-200 p-2 text-sm"
                  />
                </div>
              )}

              <button
                type="submit"
                disabled={loading}
                className="bg-clinical-teal text-white rounded-xl py-3 font-medium hover:opacity-90 transition disabled:opacity-50"
              >
                {loading ? t("triage.analyzing") : t("triage.submit")}
              </button>

              {error && <p className="text-severity-emergency text-sm">{error}</p>}
            </form>
          </div>
        )}

        {result && (
          <div className="w-full flex flex-col items-center">
            <TriageResultCard result={result} />

            {supportsImage && !observation && (
              <div className="w-full max-w-md mx-auto bg-white border border-slate-200 rounded-2xl p-5 mt-4">
                <p className="text-sm font-medium text-ink mb-2">{t("visualCheck.title")}</p>
                <input
                  type="file"
                  accept="image/jpeg,image/png,image/webp"
                  onChange={(e) => handleImageUpload(e.target.files[0])}
                  disabled={uploadingImage}
                  className="text-sm"
                />
                {uploadingImage && (
                  <p className="text-xs text-slate-500 mt-2">{t("common.loading")}</p>
                )}
              </div>
            )}

            <ObservationCard observation={observation} />
            <button type="button" onClick={() => { setResult(null); setObservation(null); setSessionId(null); setText(""); }}
              className="mt-5 text-sm text-clinical-teal hover:underline">
              {t("result.newAssessment")}
            </button>
          </div>
        )}
      </main>
      <Footer />
    </div>
  );
}
