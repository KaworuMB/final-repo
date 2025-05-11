import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import '../styles/project-details.css';
import { authFetch } from '../utils/authFetch';

function ProjectDetails() {
  const { id } = useParams();
  const [project, setProject] = useState(null);
  const [documents, setDocuments] = useState([]);
  const [members, setMembers] = useState([]);
  const [comments, setComments] = useState([]);
  const [newComment, setNewComment] = useState("");
  const [currentUsername, setCurrentUsername] = useState("");

  useEffect(() => {
    const fetchData = async () => {
      const res = await authFetch(`/api/projects/${id}/`);
      if (res.ok) {
        const data = await res.json();
        setProject(data);
        setDocuments(data.documents || []);
        setMembers(data.members || []);
        setComments(data.comments || []);
        setCurrentUsername(data.current_user?.username || "");
      }
    };

    fetchData();
  }, [id]);

  const handleCommentSubmit = async (e) => {
    e.preventDefault();
    if (!newComment.trim()) return;

    const res = await authFetch('/api/comments/', {
      method: 'POST',
      body: JSON.stringify({
        project: project.id,
        text: newComment,
      }),
    });

    if (res.ok) {
      const created = await res.json();
      setComments([created, ...comments]);
      setNewComment("");
    } else {
      alert("Не удалось добавить комментарий");
    }
  };

  const handleDeleteComment = async (commentId) => {
    if (!window.confirm("Удалить комментарий?")) return;

    const res = await authFetch(`/api/comments/${commentId}/`, {
      method: 'DELETE',
    });

    if (res.ok) {
      setComments(comments.filter(comment => comment.id !== commentId));
    } else {
      const data = await res.json();
      alert(data.detail || "Ошибка при удалении комментария");
    }
  };

  const handleDownload = async (docId, docName) => {
    try {
      const res = await authFetch(`/api/documents/${docId}/download/`);
      if (!res.ok) throw new Error();

      const blob = await res.blob();
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = docName;
      document.body.appendChild(link);
      link.click();
      link.remove();
      URL.revokeObjectURL(url);
    } catch {
      alert("Не удалось скачать файл");
    }
  };

  const handleDeleteDocument = async (docId) => {
    if (!window.confirm("Удалить документ?")) return;

    const res = await authFetch(`/api/documents/${docId}/`, { method: 'DELETE' });
    if (res.ok) {
      setDocuments(documents.filter(doc => doc.id !== docId));
    } else {
      alert("Не удалось удалить документ");
    }
  };

  const isOwner = (username) => username === project?.owner?.username;

  if (!project) return <div>Loading...</div>;

  return (
    <div className="dashboard">
      <h1 className="dashboard__title">{project.project_name}</h1>

      {/* Documents */}
      <div className="documents">
        {documents.length > 0 ? documents.map(doc => (
          <div key={doc.id} className="document-card">
            <div className="document-card__info">
              <div className="document-card__name">{doc.name}</div>
              <div className="document-card__path">{doc.file}</div>
            </div>
            <div className="document-card__actions">
              <button onClick={() => handleDownload(doc.id, doc.name)}>⬇️</button>
              <button onClick={() => handleDeleteDocument(doc.id)}>🗑️</button>
            </div>
          </div>
        )) : <p>No documents.</p>}
        <div className="dashboard__add">
          <Link to={`/projects/${id}/upload`} className="add-button">+</Link>
        </div>
      </div>

      {/* Members */}
      <div className="members">
        <Link to={`/projects/${id}/members`} className="members__title">Members</Link>
        {members.map(m => (
          <div key={m.id} className="member">
            {m.username} {isOwner(m.username) && <span title="Owner">👑</span>}
          </div>
        ))}
      </div>

      <div className="comments" style={{ marginTop: '40px' }}>
          <h2 className="section-title">Comments</h2>

          {comments.length > 0 ? comments.map(comment => (
            <div key={comment.id} style={{
              display: 'flex',
              alignItems: 'flex-start',
              marginBottom: '20px',
              gap: '12px',
              padding: '12px',
              border: '1px solid #eee',
              borderRadius: '12px',
              background: '#fafafa',
            }}>
              {/* Иконка или аватар */}
              <div style={{ fontSize: '24px', marginTop: '4px' }}>👤</div>

              {/* Контент комментария */}
              <div style={{ flexGrow: 1 }}>
                <div style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  marginBottom: '4px'
                }}>
                <div style={{ fontWeight: 'bold', whiteSpace: 'nowrap' }}>
                  {comment.username}
                  {comment.user === project.owner.id && <span title="Owner"> 👑</span>}
                  {comment.username === currentUsername && <span style={{ color: '#007bff', marginLeft: '8px' }}>(You)</span>}
                </div>
                  <div style={{ fontSize: '12px', color: '#888', whiteSpace: 'nowrap' }}>
                    {new Date(comment.created_at).toLocaleString()}
                  </div>
                </div>

                <div style={{
                  background: '#f5f5f5',
                  padding: '10px 14px',
                  borderRadius: '10px',
                  position: 'relative',
                  wordBreak: 'break-word',
                }}>
                  {comment.text}

                  {(comment.is_owner || comment.is_project_owner) && (
                    <button
                      onClick={() => handleDeleteComment(comment.id)}
                      title="Удалить комментарий"
                      style={{
                        position: 'absolute',
                        top: '6px',
                        right: '6px',
                        background: 'none',
                        border: 'none',
                        color: '#d00',
                        cursor: 'pointer',
                        fontSize: '14px'
                      }}
                    >
                      🗑️
                    </button>
                  )}
                </div>
              </div>
            </div>
          )) : (
            <p>No comments yet.</p>
          )}


          {/* Add Comment Form */}
          <form onSubmit={handleCommentSubmit} className="comment-form" style={{ marginTop: '20px', display: 'flex' }}>
            <input
              type="text"
              placeholder="Comment"
              value={newComment}
              onChange={(e) => setNewComment(e.target.value)}
              required
              className="comment-form__input"
              style={{
                flexGrow: 1,
                padding: '10px',
                borderRadius: '8px',
                border: '1px solid #ccc',
                marginRight: '10px'
              }}
            />
            <button
              type="submit"
              className="comment-form__button"
              style={{
                padding: '10px 16px',
                backgroundColor: '#007bff',
                color: '#fff',
                border: 'none',
                borderRadius: '8px',
                cursor: 'pointer'
              }}
            >
              ➤
            </button>
          </form>
        </div>


      {/* Add Comment Form
      <form onSubmit={handleCommentSubmit} className="comment-form">
        <input
          type="text"
          placeholder="Comment"
          value={newComment}
          onChange={(e) => setNewComment(e.target.value)}
          required
          className="comment-form__input"
        />
        <button type="submit" className="comment-form__button">➤</button>
      </form> */}
    </div>
  );
}

export default ProjectDetails;



