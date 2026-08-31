import React, { useState } from 'react';
import { FileUp, Loader2, CheckCircle2, AlertTriangle, X, FileText, Camera, ShieldCheck } from 'lucide-react';
import { uploadOCREvidence } from '../services/api';
import { cyberSound } from '../utils/cyberSound';

const SAMPLE_DOCS = [
  {
    name: 'FedEx_Proof_of_Delivery_GPS_Signed.pdf',
    type: 'COURIER_WAYBILL',
    label: '📦 Courier POD Receipt (FedEx GPS & Signed)',
    text: 'FEDEX TRACKING: FEDEX-98827-POD-GPS. DELIVERED TO FRONT DOOR WITH RECIPIENT SIGNATURE. LAT: 37.7749 LONG: -122.4194',
  },
  {
    name: 'Official_Itemized_Sales_Invoice_Signed.pdf',
    type: 'BILLING_INVOICE',
    label: '🧾 Itemized Merchant Invoice & Tax Receipt',
    text: 'INVOICE INV-8829-RETAIL. ITEM: Electronics Hardware $199.99. TAX: $16.00. TOTAL PAID: $215.99. AVS & CVV MATCH CONFIRMED.',
  },
  {
    name: 'Customer_Support_Acknowledgment_Chat.png',
    type: 'CUSTOMER_COMMUNICATION',
    label: '💬 Customer Signed Delivery Acknowledgement',
    text: 'CUSTOMER TICKET #4491: "I have received the order in good condition on August 20th. Thank you."',
  },
];

export default function OCREvidenceUploaderModal({ disputeId, onUploaded, onClose }) {
  const [selectedDoc, setSelectedDoc] = useState(SAMPLE_DOCS[0]);
  const [loading, setLoading] = useState(false);
  const [ocrResult, setOcrResult] = useState(null);
  const [error, setError] = useState(null);

  const handleUploadAndExtract = async () => {
    try {
      setLoading(true);
      setError(null);
      cyberSound.playClick();
      const res = await uploadOCREvidence(disputeId, {
        filename: selectedDoc.name,
        document_type: selectedDoc.type,
        raw_text: selectedDoc.text,
      });
      setOcrResult(res);
      cyberSound.playSuccess();
      setTimeout(() => {
        onUploaded();
      }, 1500);
    } catch (err) {
      console.error('OCR Upload failed:', err);
      setError('OCR Upload failed: ' + (err.response?.data?.detail || err.message));
      cyberSound.playError();
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md animate-fade-in">
      <div
        className="w-full max-w-xl rounded-3xl p-6 border shadow-2xl relative font-mono text-xs overflow-hidden"
        style={{
          background: 'linear-gradient(135deg, rgba(15, 23, 42, 0.98) 0%, rgba(9, 13, 30, 0.99) 100%)',
          borderColor: 'rgba(99, 102, 241, 0.4)',
          boxShadow: '0 25px 60px rgba(0, 0, 0, 0.8), 0 0 30px rgba(99, 102, 241, 0.15)',
        }}
      >
        <div className="flex items-center justify-between pb-3 border-b border-slate-800">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-xl bg-cyan-600/20 text-cyan-400 flex items-center justify-center border border-cyan-500/30">
              <Camera className="w-4 h-4" />
            </div>
            <div>
              <h3 className="text-sm font-bold text-white">Multimodal OCR Evidence Extractor</h3>
              <p className="text-[10px] text-slate-400">Ingest paper waybills, signatures, and physical delivery receipts</p>
            </div>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="p-1 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-colors cursor-pointer"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Document Selection / Drag Zone */}
        <div className="mt-4">
          <label className="text-[10px] text-slate-400 uppercase font-bold block mb-2">
            Select Physical Scanned Document or Simulated Waybill
          </label>
          <div className="space-y-2">
            {SAMPLE_DOCS.map((doc, idx) => {
              const isSelected = selectedDoc.name === doc.name;
              return (
                <button
                  key={idx}
                  type="button"
                  onClick={() => setSelectedDoc(doc)}
                  className={`w-full p-3 rounded-2xl border text-left flex items-start justify-between transition-all cursor-pointer ${
                    isSelected
                      ? 'bg-indigo-600/20 border-indigo-500 text-white'
                      : 'bg-slate-900/60 border-slate-800 text-slate-400 hover:text-slate-200'
                  }`}
                >
                  <div className="flex items-start gap-2.5">
                    <FileText className="w-4 h-4 text-indigo-400 mt-0.5 flex-shrink-0" />
                    <div>
                      <p className="font-bold text-xs text-slate-200">{doc.label}</p>
                      <p className="text-[10px] text-slate-500 mt-0.5">{doc.name}</p>
                      <p className="text-[9px] text-slate-400 font-mono mt-1 bg-slate-950 p-1 rounded border border-slate-800">
                        {doc.text}
                      </p>
                    </div>
                  </div>
                  {isSelected && <CheckCircle2 className="w-4 h-4 text-cyan-400 flex-shrink-0" />}
                </button>
              );
            })}
          </div>
        </div>

        {error && <p className="text-[11px] text-rose-400 mt-2">{error}</p>}

        {ocrResult && (
          <div className="mt-4 p-3.5 rounded-2xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-300 animate-fade-in">
            <div className="flex items-center gap-2 font-bold mb-1">
              <ShieldCheck className="w-4 h-4 text-emerald-400" />
              <span>OCR Extraction & Verification Succeeded</span>
            </div>
            <p className="text-[10px] text-slate-300">{ocrResult.description}</p>
            <p className="text-[9px] text-indigo-300 font-mono mt-1">
              Ref: {ocrResult.source_reference} · Category: {ocrResult.category} · Evidence #{ocrResult.evidence_id}
            </p>
          </div>
        )}

        {/* Footer Actions */}
        <div className="mt-5 pt-3 border-t border-slate-800 flex items-center justify-between">
          <span className="text-[10px] text-slate-500">Tesseract / Vision AI Engine Active</span>
          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={onClose}
              className="px-3 py-1.5 rounded-xl text-slate-400 hover:text-white cursor-pointer"
            >
              Close
            </button>
            <button
              type="button"
              disabled={loading || !!ocrResult}
              onClick={handleUploadAndExtract}
              className="px-4 py-2 rounded-xl bg-gradient-to-r from-cyan-600 to-indigo-600 hover:from-cyan-500 hover:to-indigo-500 text-white font-bold transition-all disabled:opacity-40 cursor-pointer flex items-center gap-1.5 shadow-lg shadow-cyan-600/20"
            >
              {loading ? (
                <Loader2 className="w-3.5 h-3.5 animate-spin" />
              ) : (
                <FileUp className="w-3.5 h-3.5" />
              )}
              <span>Ingest & Extract OCR</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
