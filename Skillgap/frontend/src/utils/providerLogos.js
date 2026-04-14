import courseraLogo from "../assets/images/providers/coursera.png";
import edxLogo from "../assets/images/providers/edX.png";
/*providerLogod.js - for placing the correct logo for the provider of each course */
//function normalises provider values from the backend
export function normaliseProviderName(provider){
    const value = String(provider || "").trim().toLowerCase();

    const aliases = {
        edx: "edx",
        edx_courses: "edx",
        edx_programs: "edx",
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