import React, { useEffect, useState } from 'react';
import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL;


// This component fetches and displays the confusion matrix image from the backend
function ConfusionMatrixImage({ file }) {
    const [imgSrc, setImgSrc] = useState(null);
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);
    const [showModal, setShowModal] = useState(false);

    useEffect(() => {
        if (!file) {
            setImgSrc(null);
            setError('');
            return;
        }
        const fetchImage = async () => {
            setLoading(true);
            setError('');
            setImgSrc(null);
            const formData = new FormData();
            formData.append('file', file);
            try {
                const response = await axios.post(`${API_URL}/confusion-matrix`, formData, {
                    headers: { 'Content-Type': 'multipart/form-data' },
                });
                setImgSrc(`data:image/png;base64,${response.data.image}`);
            } catch (err) {
                setError('Failed to load confusion matrix image.');
            } finally {
                setLoading(false);
            }
        };
        fetchImage();
    }, [file]);

    if (!file) return null;
    if (loading) return <p>Loading confusion matrix...</p>;
    if (error) return <p style={{ color: 'red' }}>{error}</p>;
    if (!imgSrc) return null;
    return (
        <div style={{ textAlign: 'center', margin: '24px 0' }}>
            <h4>Confusion Matrix</h4>
            <img
                src={imgSrc}
                alt="Confusion Matrix"
                style={{ maxWidth: '100%', border: '1px solid #ccc', borderRadius: '8px', cursor: 'pointer', transition: 'box-shadow 0.2s' }}
                onClick={() => setShowModal(true)}
                title="Click to enlarge"
            />
            {showModal && (
                <div className="cmatrix-modal-overlay" onClick={() => setShowModal(false)}>
                    <div className="cmatrix-modal-content" onClick={e => e.stopPropagation()}>
                        <img
                            src={imgSrc}
                            alt="Confusion Matrix Enlarged"
                            style={{ maxWidth: '90vw', maxHeight: '80vh', borderRadius: '12px', boxShadow: '0 8px 32px rgba(0,0,0,0.25)' }}
                        />
                        <button className="cmatrix-modal-close" onClick={() => setShowModal(false)}>&times;</button>
                    </div>
                </div>
            )}
        </div>
    );
}

export default ConfusionMatrixImage;
