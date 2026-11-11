
import { useEffect, useState } from "react";
import { EditorContent, useEditor } from "@tiptap/react";
import StarterKit from "@tiptap/starter-kit";
import Underline from "@tiptap/extension-underline";
import {
  FileText,
  Plus,
  Upload,
  Share2,
  Bold,
  Italic,
  Underline as UnderlineIcon,
  List,
  ListOrdered,
  Heading1,
  Heading2,
} from "lucide-react";
import "./App.css";

const API = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";
const USERS = ["alice@ajaia.test", "bob@ajaia.test"];

type Doc = {
  id: number;
  title: string;
  content: string;
  owner: string;
  shared: boolean;
};

function displayName(email: string) {
  if (email === USERS[0]) return "Alice";
  if (email === USERS[1]) return "Bob";
  return email;
}

export default function App() {
  const [user, setUser] = useState(USERS[0]);
  const [owned, setOwned] = useState<Doc[]>([]);
  const [shared, setShared] = useState<Doc[]>([]);
  const [selected, setSelected] = useState<Doc | null>(null);
  const [title, setTitle] = useState("");
  const [content, setContent] = useState("");
  const [status, setStatus] = useState("Changes saved");
  const [loading, setLoading] = useState(false);

  const editor = useEditor({
    extensions: [StarterKit, Underline],
    content: "",
    onUpdate: ({ editor }) => {
      setContent(editor.getHTML());
      setStatus("Unsaved changes");
    },
    editorProps: {
      attributes: {
        class: "editor-content",
        spellcheck: "true",
        "aria-label": "Document editor",
      },
    },
  });
  
  async function request(path: string, options: RequestInit = {}) {
    const response = await fetch(`${API}${path}`, {
      ...options,
      headers: {
        "X-User-Email": user,
        ...(options.body instanceof FormData
          ? {}
          : { "Content-Type": "application/json" }),
        ...options.headers,
      },
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({}));
      throw new Error(error.detail || "Unable to complete your request.");
    }

    return response.json();
  }

  async function loadDocuments() {
    try {
      const data = await request("/documents");
      setOwned(data.owned);
      setShared(data.shared);

      if (selected) {
        const updated = [...data.owned, ...data.shared].find(
          (doc: Doc) => doc.id === selected.id
        );

        if (!updated) {
          setSelected(null);
          setTitle("");
          setContent("");
          editor?.commands.setContent("");
        }
      }
    } catch (error) {
      alert(
        error instanceof Error
          ? error.message
          : "Unable to retrieve your documents."
      );
    }
  }

  useEffect(() => {
    loadDocuments();
    setSelected(null);
    setTitle("");
    setContent("");
    editor?.commands.setContent("");
  }, [user]);

  async function createDocument() {
    try {
      const result = await request("/documents", {
        method: "POST",
        body: JSON.stringify({
          title: "Untitled document",
          content: "",
        }),
      });

      await loadDocuments();
      await openDocument(result.id);
    } catch (error) {
      alert(
        error instanceof Error
          ? error.message
          : "Unable to create the document."
      );
    }
  }

  async function openDocument(id: number) {
    try {
      const doc = await request(`/documents/${id}`);

      setSelected({
        ...doc,
        shared: doc.owner !== user,
      });
      setTitle(doc.title);
      setContent(doc.content || "");
      editor?.commands.setContent(doc.content || "");
    } catch (error) {
      alert(
        error instanceof Error
          ? error.message
          : "Unable to open the document."
      );
    }
  }

  useEffect(() => {
    if (!selected) return;

    setStatus("Saving changes…");

    const timer = setTimeout(async () => {
      try {
        await request(`/documents/${selected.id}`, {
          method: "PUT",
          body: JSON.stringify({ title, content }),
        });

        setStatus("Changes saved");
        loadDocuments();
      } catch {
        setStatus("Unable to save changes. Please retry.");
      }
    }, 800);

    return () => clearTimeout(timer);
  }, [title, content, selected?.id]);

  async function uploadFile(file?: File) {
    if (!file) return;

    const form = new FormData();
    form.append("file", file);

    try {
      setLoading(true);

      const result = await request("/documents/upload", {
        method: "POST",
        body: form,
      });

      await loadDocuments();
      await openDocument(result.id);
    } catch (error) {
      alert(
        error instanceof Error
          ? error.message
          : "Unable to import the selected file."
      );
    } finally {
      setLoading(false);
    }
  }

  async function shareDocument() {
    if (!selected) return;

    const defaultEmail = user === USERS[0] ? USERS[1] : USERS[0];

    const email = window.prompt(
      "Enter the email address of the person you want to share this document with (Alice or Bob):",
      defaultEmail
    );

    if (!email) return;

    try {
      await request(`/documents/${selected.id}/share`, {
        method: "POST",
        body: JSON.stringify({
          email: email.trim().toLowerCase(),
        }),
      });

      alert(`Document successfully shared with ${displayName(email.trim().toLowerCase())}.`);
      await loadDocuments();
    } catch (error) {
      alert(
        error instanceof Error
          ? error.message
          : "Unable to share the document."
      );
    }
  }

  function format(command: () => void) {
    command();
  }

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-icon">
            <FileText size={23} />
          </div>
          <span>
            Ajaia<span className="brand-light">Docs</span>
          </span>
        </div>

        <button className="new-doc" onClick={createDocument}>
          <Plus size={18} /> New document
        </button>

        <div className="side-section">
          <div className="section-label">WORKSPACE</div>
          <div className="side-link active">
            <FileText size={17} /> My documents
          </div>
          <div className="section-label shared-label">SHARED WITH ME</div>
        </div>

        <div className="document-list">
          {shared.map((doc) => (
            <button
              key={doc.id}
              className={`doc-link ${
                selected?.id === doc.id ? "selected" : ""
              }`}
              onClick={() => openDocument(doc.id)}
            >
              <FileText size={16} />
              <span>{doc.title}</span>
            </button>
          ))}

          {shared.length === 0 && (
            <p className="empty-sidebar">No shared documents</p>
          )}
        </div>

        <div className="side-section">
          <div className="section-label">MY DOCUMENTS</div>
        </div>

        <div className="document-list">
          {owned.map((doc) => (
            <button
              key={doc.id}
              className={`doc-link ${
                selected?.id === doc.id ? "selected" : ""
              }`}
              onClick={() => openDocument(doc.id)}
            >
              <FileText size={16} />
              <span>{doc.title}</span>
            </button>
          ))}

          {owned.length === 0 && (
            <p className="empty-sidebar">No documents yet</p>
          )}
        </div>

        <div className="sidebar-bottom">
          <div className="account-switcher">
            <div className="account-label">WORKSPACE ACCOUNT</div>

            <div className="account-profile">
              <div className="account-avatar">
                {user === USERS[0] ? "A" : "B"}
              </div>

              <div className="account-details">
                <strong>{displayName(user)}</strong>
                <span>{user}</span>
              </div>

              <span className="account-indicator" />
            </div>

            <label className="switch-label" htmlFor="demo-account">
              Switch account
            </label>

            <div className="account-select-wrap">
              <select
                id="demo-account"
                className="account-select"
                value={user}
                onChange={(event) => setUser(event.target.value)}
                aria-label="Switch workspace account"
              >
                {USERS.map((workspaceUser) => (
                  <option key={workspaceUser} value={workspaceUser}>
                    {displayName(workspaceUser)}
                  </option>
                ))}
              </select>
            </div>

            <p className="account-hint">
              Switch accounts to view documents and shared access for each user.
            </p>
          </div>
        </div>
      </aside>

      <main className="main-area">
        <header className="topbar">
          <div className="breadcrumb">
            <span>Workspace</span>
            <span>/</span>
            <strong>
              {selected ? title || "Untitled document" : "Documents"}
            </strong>
          </div>

          <div className="top-actions">
            <span className="save-status">
              <span className="status-dot" />
              {status}
            </span>

            {selected && !selected.shared && (
              <button className="share-button" onClick={shareDocument}>
                <Share2 size={16} /> Share
              </button>
            )}
          </div>
        </header>

        {!selected ? (
          <section className="welcome">
            <div className="welcome-heading">
              <div>
                <p className="eyebrow">YOUR WORKSPACE</p>
                <h1>Your documents, organized.</h1>
                <p className="welcome-subtitle">
                  Create, edit, organize, and share documents in one workspace.
                </p>
              </div>

              <button className="primary-button" onClick={createDocument}>
                <Plus size={18} /> Create document
              </button>
            </div>

            <div className="quick-actions">
              <button className="action-card" onClick={createDocument}>
                <div className="action-icon purple">
                  <Plus size={22} />
                </div>
                <strong>Blank document</strong>
                <span>Create a new document from scratch</span>
              </button>

              <label className="action-card upload-card">
                <div className="action-icon green">
                  <Upload size={22} />
                </div>
                <strong>Import a file</strong>
                <span>
                  {loading
                    ? "Importing file…"
                    : "Import a TXT or Markdown file"}
                </span>
                <input
                  type="file"
                  accept=".txt,.md,text/plain,text/markdown"
                  hidden
                  onChange={(event) => uploadFile(event.target.files?.[0])}
                />
              </label>
            </div>

            <div className="recent-heading">
              <h2>Recent documents</h2>
              <span>{owned.length + shared.length} documents</span>
            </div>

            <div className="recent-list">
              {[...owned, ...shared].map((doc) => (
                <button
                  className="recent-row"
                  key={doc.id}
                  onClick={() => openDocument(doc.id)}
                >
                  <div className="recent-file-icon">
                    <FileText size={19} />
                  </div>

                  <div className="recent-file-name">
                    <strong>{doc.title}</strong>
                    <span>
                      {doc.shared
                        ? `Shared by ${displayName(doc.owner)}`
                        : "Owned by you"}
                    </span>
                  </div>

                  <span className="recent-tag">
                    {doc.shared ? "Shared" : "Private"}
                  </span>
                </button>
              ))}

              {owned.length + shared.length === 0 && (
                <div className="empty-state">
                  You don't have any documents yet. Create a new document or
                  import an existing file to get started.
                </div>
              )}
            </div>
          </section>
        ) : (
          <section className="editor-page">
            <div className="editor-header">
              <input
                className="document-title"
                value={title}
                onChange={(event) => setTitle(event.target.value)}
                aria-label="Document title"
                placeholder="Untitled document"
              />

              <div className="editor-meta">
                <span>
                  {selected.shared
                    ? `Shared by ${displayName(selected.owner)}`
                    : "Owned by you"}
                </span>
                <span>•</span>
                <span>{status}</span>
              </div>
            </div>

            <div className="toolbar">
              <button
                title="Bold"
                aria-label="Bold"
                onClick={() =>
                  format(() => editor?.chain().focus().toggleBold().run())
                }
              >
                <Bold size={17} />
              </button>

              <button
                title="Italic"
                aria-label="Italic"
                onClick={() =>
                  format(() => editor?.chain().focus().toggleItalic().run())
                }
              >
                <Italic size={17} />
              </button>

              <button
                title="Underline"
                aria-label="Underline"
                onClick={() =>
                  format(() =>
                    editor?.chain().focus().toggleUnderline().run()
                  )
                }
              >
                <UnderlineIcon size={17} />
              </button>

              <span className="toolbar-divider" />

              <button
                title="Heading 1"
                aria-label="Heading 1"
                onClick={() =>
                  format(() =>
                    editor?.chain().focus().toggleHeading({ level: 1 }).run()
                  )
                }
              >
                <Heading1 size={19} />
              </button>

              <button
                title="Heading 2"
                aria-label="Heading 2"
                onClick={() =>
                  format(() =>
                    editor?.chain().focus().toggleHeading({ level: 2 }).run()
                  )
                }
              >
                <Heading2 size={19} />
              </button>

              <span className="toolbar-divider" />

              <button
                title="Bulleted list"
                aria-label="Bulleted list"
                onClick={() =>
                  format(() =>
                    editor?.chain().focus().toggleBulletList().run()
                  )
                }
              >
                <List size={18} />
              </button>

              <button
                title="Numbered list"
                aria-label="Numbered list"
                onClick={() =>
                  format(() =>
                    editor?.chain().focus().toggleOrderedList().run()
                  )
                }
              >
                <ListOrdered size={18} />
              </button>

              <span className="toolbar-spacer" />

              <label className="toolbar-upload" title="Import TXT or Markdown">
                <Upload size={16} /> Import
                <input
                  type="file"
                  accept=".txt,.md"
                  hidden
                  onChange={(event) => uploadFile(event.target.files?.[0])}
                />
              </label>
            </div>

            <div className="paper-wrap">
              <div className="paper">
                <EditorContent editor={editor} />
              </div>
            </div>
          </section>
        )}
      </main>
    </div>
  );
}
