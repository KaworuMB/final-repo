import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import '../styles/project-members.css';
import { authFetch } from '../utils/authFetch';

function ProjectMembers() {
  const { id } = useParams();
  const [members, setMembers] = useState([]);
  const [email, setEmail] = useState('');
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [currentUserId, setCurrentUserId] = useState(null);
  const [ownerId, setOwnerId] = useState(null);

  useEffect(() => {
    const fetchMembers = async () => {
      try {
        const response = await authFetch(`/api/projects/${id}/members/`, {
          method: 'GET',
        });

        if (response.status === 401) {
          window.location.href = '/login';
          return;
        }

        if (!response.ok) {
          throw new Error('Failed to fetch members');
        }

        const data = await response.json();
        setMembers(data.members);
        setCurrentUserId(data.current_user_id);
        setOwnerId(data.owner_id);
      } catch (err) {
        console.error('Error fetching members:', err);
        setError('Something went wrong. Please try again later.');
      } finally {
        setLoading(false);
      }
    };

    fetchMembers();
  }, [id]);

  const handleInvite = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const response = await authFetch(`/api/projects/${id}/members/invite/`, {
        method: 'POST',
        body: JSON.stringify({ email }),
      });

      const data = await response.json();

      if (response.ok) {
        setMessages([{ text: data.detail || `Invite sent to ${email}`, type: 'success' }]);
        setEmail('');
      } else {
        setMessages([{ text: data.detail || 'Failed to send invite', type: 'error' }]);
      }
    } catch (err) {
      console.error('Error inviting member:', err);
      setError('Something went wrong. Please try again later.');
    } finally {
      setLoading(false);
    }
  };

  const removeMember = async (memberId) => {
    try {
      const response = await authFetch(`/api/projects/${id}/members/${memberId}/`, {
        method: 'DELETE',
      });

      if (response.ok) {
        setMembers(members.filter(m => m.id !== memberId));
      } else {
        const data = await response.json();
        setMessages([{ text: data.detail || 'Failed to remove member', type: 'error' }]);
      }
    } catch (err) {
      console.error('Error removing member:', err);
      setError('Something went wrong. Please try again later.');
    }
  };

  return (
    <div className="dashboard">
      <h1 className="dashboard__title">Project Members</h1>

      {loading && <p>Loading...</p>}
      {error && <p className="dashboard__error">{error}</p>}

      {messages.length > 0 && (
        <ul className="messages">
          {messages.map((msg, index) => (
            <li key={index} className={`message ${msg.type}`}>{msg.text}</li>
          ))}
        </ul>
      )}

      <div className="member-list">
        {members.length > 0 ? (
          members.map(m => {
            const isSelf = m.id === currentUserId;
            const isOwner = m.id === ownerId;
            const currentUserIsOwner = currentUserId === ownerId;

            return (
              <div className="member" key={m.id}>
                <span className="member__name">
                  {m.username} {isOwner && <span title="Owner">👑</span>}
                </span>

                {(!isOwner && (isSelf || currentUserIsOwner)) && (
                  <button className="member__remove" onClick={() => removeMember(m.id)}>
                    🗑️
                  </button>
                )}
              </div>
            );
          })
        ) : (
          <p>No members yet.</p>
        )}
      </div>

      {currentUserId === ownerId && (
          <form onSubmit={handleInvite} className="invite-form">
            <input
              type="email"
              value={email}
              onChange={e => setEmail(e.target.value)}
              className="invite-form__input"
              placeholder="Enter email to invite"
              required
            />
            <button type="submit" className="invite-form__button">Invite</button>
          </form>
        )}
    </div>
  );
}

export default ProjectMembers;