interface CardProps {
  children: React.ReactNode;
}

function Card(props: CardProps) {
  const { children } = props;
  return (
    <div
      className="mx-auto card h-lg-100 h-sm-50 w-100 w-lg-50"
      style={{
        width: "100%",
        maxWidth: "1000px",
        marginBottom: "5px",
        minHeight: "50px",
        maxHeight: "900px",
      }}
    >
      <div className="card-body">{children}</div>
    </div>
  );
}

interface CardBodyProps {
  title?: string;
  text1?: string;
  text2?: string;
  text3?: string;
  text4?: string;
  text5?: string;
  text6?: string;
  text7?: string;
}

export function CardBody(props: CardBodyProps) {
  const { title, text1, text2, text3, text4, text5, text6, text7 } = props;

  return (
    <>
      <h5 className="card-title text">{title}</h5>
      {text1 && <p className="card-text">{text1}</p>}
      {text2 && <p className="card-text">{text2}</p>}
      {text3 && <p className="card-text">{text3}</p>}
      {text4 && <p className="card-text">{text4}</p>}
      {text5 && <p className="card-text">{text5}</p>}
      {text6 && <p className="card-text">{text6}</p>}
      {text7 && <p className="card-text">{text7}</p>}
    </>
  );
}

export default Card;
