function Navbar() {
  return (
    <nav
      className="navbar navbar-expand-lg navbar-light bg-light rounded shadow-sm mt-2 mx-auto px-3"
      style={{ width: "95%", maxWidth: "100%" }}
    >
      <div className="container-fluid d-flex flex-wrap align-items-center justify-content-between gap-2">
        {/* Marca / Título */}
        <a
          className="navbar-brand d-flex align-items-center gap-2 mb-0"
          href="#"
        >
          <div className="d-flex flex-column align-items-start">
            <span className="h4 mb-0">Space Discovery</span>
          </div>
        </a>
      </div>
    </nav>
  );
}

export default Navbar;
