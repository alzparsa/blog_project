export default function StepCard({ number, title, description }) {
    return (
        <div>
            <p> {number}</p>
            <h3>{title}</h3>
            <p>{description}</p>
        </div>
    );
}