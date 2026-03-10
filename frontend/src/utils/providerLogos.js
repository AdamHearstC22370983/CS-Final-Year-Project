import courseraLogo from "../assets/images/providers/coursera.png";
import edxLogo from "../assets/images/providers/edX.png";
/*providerLogod.js - for placing the correct logo for the provider of each course so that
the user knows what website they will be going to before visiting the link*/

//function normalises provider values fomr the backend
export function normaliseProviderName(provider){
    const value = String(provider || "").trim().toLowerCase();

    const aliases = {
        edx: "edx",
        edx_courses: "edx",
        coursera: "coursera",
    };

    return aliases[value] || value;
}
//function returns the display label the user should see
export function getProviderDisplayName(provider){
    const normalised = normaliseProviderName(provider);

    const displayNames = {
        coursera: "Coursera",
        edx: "edX",
    };

    return displayNames[normalised] || provider || "Unknown Provider";
}
//function returns the correct provider logo based on the normalised value
export function getProviderLogo(provider){
  const normalised = normaliseProviderName(provider);

  const logos = {
    coursera: courseraLogo,
    edx: edxLogo,
  };

  return logos[normalised] || null;
}