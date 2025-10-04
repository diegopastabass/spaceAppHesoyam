import React from "react";

const ErrorPage: React.FC = () => {
  return (
    <main className="min-vh-100 d-flex align-items-center bg-body-tertiary">
      <div className="container py-5">
        <div className="row justify-content-center">
          <div className="col-12 col-md-10 col-lg-8 text-center">
            <span className="badge text-bg-danger mb-3">Error 404</span>
            <h1 className="display-3 fw-bold mb-2">Página no encontrada</h1>
            <p className="lead text-body-secondary mb-4">
              Lo sentimos, la página que buscas no existe o fue movida.
            </p>

            <div className="d-flex gap-2 justify-content-center">
              <button
                type="button"
                className="btn btn-primary"
                onClick={() => window.history.back()}
              >
                Volver
              </button>
              <a className="btn btn-outline-secondary" href="/mantenimiento/">
                Ir al inicio
              </a>
            </div>

            <hr className="my-5" />

            <div className="d-flex align-items-center justify-content-center gap-3 text-body-tertiary">
              <div className="display-6 fw-bold">404</div>
              <div className="vr" />
              <div>
                <div className="small">Código de estado</div>
                <div className="small">No encontrado</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>
  );
};

export default ErrorPage;
