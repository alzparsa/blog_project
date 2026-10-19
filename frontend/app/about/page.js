import StepCard from "../../components/StepCard";
import NavLink from "../../components/NavLink";

const steps  =  [
    {number: "1", title: "Follow a category", description: "Fitness, coding, writing, music, or anything else you care about"},
    {number: "2", title: "Share your progress", description: "Post a session, a milestone, a struggle, or a question"},
    {number: "3", title: "Find your people", description: "Everyone following that category sees your posts and can comment"},
    {number: "4", title: "Pass it on", description: "When a post moves you, hit Inspired me and let the author know"}
];

const beliefs = [
    {number: "1", title: "Progress over perfection", description: "Small steps count"},
    {number: "2", title: "Example over advice", description: "Showing beats telling"},
    {number: "3", title: "Supportive by default", description: "Questions are welcome, and beginners are the point"},
    {number: "4", title: "Together moves faster", description: "A shared goal makes the hard days easier"}
];

export default function AboutPage() {
    return (
        <main>
            <section>
                <h1>Start before you feel ready.</h1>
                <p>Inspired is a place to share your progress, learn from others walking the same path, and move toward a goal alongside people who get it.</p>
            </section>
            <section>
                <h2>The problem</h2>
                <p>Most of us have something we want to start: getting fit, learning to code, writing a book, picking up an instrument. And most of us hit the same wall: nobody around us is doing it.</p>
                <p>No one to ask. No one to compare notes with. No one who understands why a 10-minute walk or a single paragraph counts as a win.</p>
            </section>
            <section>
                <h2>What Inspired is</h2>
                <p>Inspired is a blog community built on one idea: 
                    <strong>seeing someone else make progress makes your own start feel possible.</strong></p>
                <p>You follow the categories that matter to you, share what you’re doing, ask questions, and see what everyone else in that space is up to. No highlight reels, just real progress, one post at a time.</p>
            </section>
            <section>
                <h2>How it works</h2>
                {steps.map((step) => (
                    <StepCard 
                        key={step.number}
                        number={step.number}
                        title={step.title}
                        description={step.description}
                    />
                ))}
            </section>
            <section >
                <h2>The “Inspired me” button</h2>
                <p>We replaced the like button on purpose. A like says “I saw this.” Inspired me says “this made me want to do something.” The people you inspire are the stat that matters here, not follower counts.</p>
                <button>Inspired me</button>
            </section>
            <section>
                <h2>Teams</h2>
                <p>Working toward something with others? Create a team, from a small accountability group to a large community, and share your progress in one place. See what your teammates are working on, and stay aware of other teams’ projects too.</p>
            </section>
            <section>
                <h2>What we believe</h2>
                {beliefs.map((belief) => (
                    <StepCard 
                        key={belief.number  }
                        number={belief.number}
                        title={belief.title}
                        description={belief.description}
                    />
                ))}
            </section>
            <section>
                <p><strong>Ready to start?</strong> Create your account and follow your first category.</p>
                <NavLink href="/login">Sign up</NavLink>
                <NavLink href="/categories">Browse categories</NavLink>
            </section>
        </main>
    );
}