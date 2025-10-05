const Loading = () => {
  return (
    <div className="d-flex flex-column justify-content-center align-items-center vh-100">
      <div className="spinner-border text-primary" role="status">
        <span className="visually-hidden">Cargando...</span>
      </div>

      <p className="mt-3 fs-5 fw-semibold">Cargando...</p>
      <img
        src="/src/assets/Logo.png"
        alt="HESOYAM Logo"
        width={200}
        height={100}
      />
      <footer className="d-flex flex-wrap justify-content-between align-items-center py-3 px-4 border-top">
        <p className="mb-0 text-body-secondary">&copy; 2025 HESOYAM.</p>
      </footer>
    </div>
  );
};

export default Loading;
