import React, { useEffect, useRef, useState } from 'react';
import { Modal, Button } from 'react-bootstrap';
import '@fortawesome/fontawesome-free/css/all.min.css';
import './NodeVisualization.css';

interface NodeData {
  id: string;
  type: 'question' | 'pdf';
  label: string;
  question?: string;
  pdfs?: string[];
  x?: number;
  y?: number;
}

interface NodeVisualizationProps {
  data: NodeData[];
  onNodeClick?: (node: NodeData) => void;
  onGoToChat?: () => void;
}

const NodeVisualization: React.FC<NodeVisualizationProps> = ({ 
  data, 
  onNodeClick, 
  onGoToChat 
}) => {
  const svgRef = useRef<SVGSVGElement>(null);
  const [selectedNode, setSelectedNode] = useState<NodeData | null>(null);
  const [showModal, setShowModal] = useState(false);

  // Usar data si está disponible, sino usar datos de ejemplo
  const nodeData: NodeData[] = data.length > 0 ? data : [
    {
      id: 'p1',
      type: 'question' as const,
      label: 'P1',
      question: '¿Cuáles son las principales misiones biológicas de la NASA y qué objetivos tienen?',
      pdfs: ['mission_bio_2023.pdf', 'nasa_biological_research.pdf', 'space_biology_overview.pdf'],
      x: 400,
      y: 300
    },
    {
      id: 'bpe',
      type: 'pdf' as const,
      label: 'BPE',
      x: 200,
      y: 200
    },
    {
      id: 'pdf1',
      type: 'pdf' as const,
      label: 'PDF1',
      x: 200,
      y: 400
    },
    {
      id: 'rag',
      type: 'pdf' as const,
      label: 'RAG',
      x: 600,
      y: 300
    }
  ];

  const handleNodeClick = (node: NodeData) => {
    if (node.type === 'question') {
      setSelectedNode(node);
      setShowModal(true);
    }
    if (onNodeClick) {
      onNodeClick(node);
    }
  };

  const handleCloseModal = () => {
    setShowModal(false);
    setSelectedNode(null);
  };

  const handleGoToChat = () => {
    handleCloseModal();
    if (onGoToChat) {
      onGoToChat();
    }
  };

  useEffect(() => {
    const svg = svgRef.current;
    if (!svg) return;

    // Limpiar SVG
    svg.innerHTML = '';

    // Crear grupo para los elementos
    const g = document.createElementNS('http://www.w3.org/2000/svg', 'g');
    svg.appendChild(g);

    // Dibujar conexiones primero (para que estén detrás de los nodos)
    nodeData.forEach(node => {
      if (node.type === 'question') {
        // Conectar nodo principal con otros nodos
        nodeData.forEach(otherNode => {
          if (otherNode.id !== node.id) {
            const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
            line.setAttribute('x1', node.x!.toString());
            line.setAttribute('y1', node.y!.toString());
            line.setAttribute('x2', otherNode.x!.toString());
            line.setAttribute('y2', otherNode.y!.toString());
            line.setAttribute('stroke', '#6c757d');
            line.setAttribute('stroke-width', '2');
            line.setAttribute('opacity', '0.6');
            g.appendChild(line);
          }
        });
      }
    });

    // Dibujar nodos
    nodeData.forEach(node => {
      // Crear grupo para el nodo
      const nodeGroup = document.createElementNS('http://www.w3.org/2000/svg', 'g');
      nodeGroup.setAttribute('transform', `translate(${node.x}, ${node.y})`);
      nodeGroup.style.cursor = 'pointer';

      if (node.type === 'question') {
        // Nodo principal circular
        const circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
        circle.setAttribute('r', '40');
        circle.setAttribute('fill', '#007bff');
        circle.setAttribute('stroke', '#0056b3');
        circle.setAttribute('stroke-width', '3');
        nodeGroup.appendChild(circle);

        // Texto del nodo
        const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
        text.setAttribute('text-anchor', 'middle');
        text.setAttribute('dy', '0.35em');
        text.setAttribute('fill', 'white');
        text.setAttribute('font-size', '16');
        text.setAttribute('font-weight', 'bold');
        text.textContent = node.label;
        nodeGroup.appendChild(text);
      } else {
        // Nodos PDF rectangulares
        const rect = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
        rect.setAttribute('width', '60');
        rect.setAttribute('height', '40');
        rect.setAttribute('x', '-30');
        rect.setAttribute('y', '-20');
        rect.setAttribute('fill', '#28a745');
        rect.setAttribute('stroke', '#1e7e34');
        rect.setAttribute('stroke-width', '2');
        rect.setAttribute('rx', '5');
        nodeGroup.appendChild(rect);

        // Texto del nodo PDF
        const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
        text.setAttribute('text-anchor', 'middle');
        text.setAttribute('dy', '0.35em');
        text.setAttribute('fill', 'white');
        text.setAttribute('font-size', '12');
        text.setAttribute('font-weight', 'bold');
        text.textContent = node.label;
        nodeGroup.appendChild(text);
      }

      // Agregar evento de click
      nodeGroup.addEventListener('click', () => handleNodeClick(node));

      // Efecto hover
      nodeGroup.addEventListener('mouseenter', () => {
        nodeGroup.style.transform = `translate(${node.x}px, ${node.y}px) scale(1.1)`;
        nodeGroup.style.transition = 'transform 0.2s ease';
      });

      nodeGroup.addEventListener('mouseleave', () => {
        nodeGroup.style.transform = `translate(${node.x}px, ${node.y}px) scale(1)`;
      });

      g.appendChild(nodeGroup);
    });


  }, [data]);

  return (
    <div className="node-visualization-container">
      <div className="d-flex justify-content-between align-items-center mb-3">
        <h4>Visualización de Consultas RAG</h4>
        <small className="text-muted">Haz clic en P1 para ver detalles</small>
      </div>
      
      <div className="border rounded p-3 bg-light">
        <svg
          ref={svgRef}
          width="100%"
          height="600"
          viewBox="0 0 800 600"
          className="node-svg"
        >
          {/* El contenido se genera dinámicamente */}
        </svg>
      </div>

      {/* Modal profesional para mostrar detalles de la pregunta */}
      <Modal show={showModal} onHide={handleCloseModal} size="xl" centered>
        <Modal.Header className="bg-gradient-primary text-white border-0">
          <div className="d-flex align-items-center">
            <div className="me-3">
              <div className="bg-white bg-opacity-20 rounded-circle p-2">
                <i className="fas fa-question-circle fs-4"></i>
              </div>
            </div>
            <div>
              <Modal.Title className="mb-0">Detalles de la Consulta RAG</Modal.Title>
              <small className="opacity-75">Análisis de fuentes y contexto</small>
            </div>
          </div>
          <Button 
            variant="link" 
            className="text-white p-0 ms-auto"
            onClick={handleCloseModal}
            style={{ fontSize: '1.5rem' }}
          >
            <i className="fas fa-times"></i>
          </Button>
        </Modal.Header>
        
        <Modal.Body className="p-4">
          {selectedNode && (
            <div className="row">
              {/* Información de la pregunta */}
              <div className="col-12 mb-4">
                <div className="card border-0 shadow-sm">
                  <div className="card-header bg-primary bg-opacity-10 border-0">
                    <h5 className="mb-0 text-primary">
                      <i className="fas fa-search me-2"></i>
                      Consulta: {selectedNode.label}
                    </h5>
                  </div>
                  <div className="card-body">
                    <p className="mb-0 fs-6 text-muted">{selectedNode.question}</p>
                  </div>
                </div>
              </div>

              {/* Estadísticas */}
              <div className="col-12 mb-4">
                <div className="row g-3">
                  <div className="col-md-4">
                    <div className="card border-0 shadow-sm h-100">
                      <div className="card-body text-center">
                        <div className="text-primary mb-2">
                          <i className="fas fa-file-pdf fs-2"></i>
                        </div>
                        <h4 className="text-primary mb-1">{selectedNode.pdfs?.length || 0}</h4>
                        <small className="text-muted">Documentos analizados</small>
                      </div>
                    </div>
                  </div>
                  <div className="col-md-4">
                    <div className="card border-0 shadow-sm h-100">
                      <div className="card-body text-center">
                        <div className="text-success mb-2">
                          <i className="fas fa-brain fs-2"></i>
                        </div>
                        <h4 className="text-success mb-1">RAG</h4>
                        <small className="text-muted">Sistema de recuperación</small>
                      </div>
                    </div>
                  </div>
                  <div className="col-md-4">
                    <div className="card border-0 shadow-sm h-100">
                      <div className="card-body text-center">
                        <div className="text-warning mb-2">
                          <i className="fas fa-rocket fs-2"></i>
                        </div>
                        <h4 className="text-warning mb-1">NASA</h4>
                        <small className="text-muted">Fuente oficial</small>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Lista de PDFs */}
              <div className="col-12">
                <h6 className="mb-3 text-dark">
                  <i className="fas fa-folder-open me-2 text-primary"></i>
                  Documentos utilizados para la respuesta
                </h6>
                <div className="row g-3">
                  {selectedNode.pdfs?.map((pdf, index) => (
                    <div key={index} className="col-md-6">
                      <div className="card border-0 shadow-sm h-100 hover-lift">
                        <div className="card-body d-flex align-items-center">
                          <div className="me-3">
                            <div className="bg-danger bg-opacity-10 rounded p-2">
                              <i className="fas fa-file-pdf text-danger fs-4"></i>
                            </div>
                          </div>
                          <div className="flex-grow-1">
                            <h6 className="mb-1 text-truncate">{pdf}</h6>
                            <small className="text-muted">Documento científico</small>
                          </div>
                          <div className="ms-2">
                            <Button 
                              variant="outline-primary" 
                              size="sm"
                              className="rounded-pill"
                            >
                              <i className="fas fa-eye me-1"></i>
                              Ver
                            </Button>
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}
        </Modal.Body>
        
        <Modal.Footer className="bg-light border-0 p-4">
          <div className="d-flex justify-content-between w-100">
            <Button 
              variant="outline-secondary" 
              onClick={handleCloseModal}
              className="px-4"
            >
              <i className="fas fa-times me-2"></i>
              Cerrar
            </Button>
            <Button 
              variant="primary" 
              onClick={handleGoToChat}
              className="px-4 rounded-pill"
            >
              <i className="fas fa-comments me-2"></i>
              Ir al Chat
            </Button>
          </div>
        </Modal.Footer>
      </Modal>
    </div>
  );
};

export default NodeVisualization;
