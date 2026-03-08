//UploadCard.jsx
function UploadCard({
  title,
  description,
  file,
  onFileChange,
  accept = ".pdf,.docx,.txt",
}) {
  return (
    <div className="card shadow-sm h-100 border-0">
      <div className="card-body">
        <h5 className="card-title">{title}</h5>
        <p className="text-muted">{description}</p>

        <input
          type="file"
          className="form-control"
          accept={accept}
          onChange={onFileChange}
        />

        {file && (
          <div className="mt-3 small text-success">
            Selected: <strong>{file.name}</strong>
          </div>
        )}
      </div>
    </div>
  );
}
export default UploadCard;