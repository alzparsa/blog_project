import NavLink from "./NavLink";



// logo,                                                                           about, feed, teams, categories,                                                                     login

const NavItemsMiddle= [
    {number:"1",href: "/about", label: "About"},
    {number:"2",href: "/feed", label: "Feed"},
    {number:"3",href: "/teams", label: "My Teams"},
    {number:"4",href: "/categories", label: "My Categories"},
]
const NavItemsRight= [
    {number:"5",href: "/login", label: "Login"},
    {number:"6",href: "/signup", label: "Sign Up"},
]

export default function Header() {
    return (
        <header className="row distributed-between">
            <div className="row">
                <NavLink href="/">
                    <h1>Inspired!</h1>
                </NavLink>
            </div>
            <div className="row">
                {NavItemsMiddle.map((item) => (
                    <NavLink key={item.number} href={item.href}>
                        {item.label}
                    </NavLink>
                ))}
            </div>
            <div className="row">
                {NavItemsRight.map((item) => (
                    <NavLink key={item.number} href={item.href}>
                        {item.label}
                    </NavLink>
                ))}
            </div>
            
        </header>
    );
}