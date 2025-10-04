const Loading = () => {
  return (
    <div className="d-flex flex-column justify-content-center align-items-center vh-100">
      <div className="spinner-border text-primary" role="status">
        <span className="visually-hidden">Cargando...</span>
      </div>

      <p className="mt-3 fs-5 fw-semibold">Cargando...</p>
      <footer className="d-flex flex-wrap justify-content-between align-items-center py-3 px-4 border-top">
        <p className="mb-0 text-body-secondary">&copy; 2025 JTE Analytics.</p>
      </footer>
    </div>
  );
};

export default Loading;
