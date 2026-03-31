// src/components/ui/SchemeCard.jsx
import { useNavigate } from "react-router-dom"

const CATEGORY_COLORS = {
  education  : "bg-blue-100 text-blue-800",
  agriculture: "bg-green-100 text-green-800",
  health     : "bg-red-100 text-red-800",
  pension    : "bg-amber-100 text-amber-800",
  women      : "bg-pink-100 text-pink-800",
  other      : "bg-gray-100 text-gray-700",
}

// ── Map each category to your local image ─────────────────────────
const CATEGORY_IMAGES = {
  education  : "/images/education.jpg",
  agriculture: "/images/agriculture.jpg",
  health     : "/images/health.jpg",
  pension    : "/images/pension.jpg",
  women      : "/images/women.jpg",
  other      : "/images/health.jpg",
}

export default function SchemeCard({ scheme, isBestMatch = false }) {
  const navigate   = useNavigate()
  const colorClass = CATEGORY_COLORS[scheme.category] || CATEGORY_COLORS.other
  const imageSrc   = CATEGORY_IMAGES[scheme.category]  || CATEGORY_IMAGES.other

  return (
    <div
      className={`card relative hover:shadow-md transition-shadow cursor-pointer flex flex-col
                  ${isBestMatch ? "border-2 border-accent" : ""}`}
      onClick={() => navigate(`/scheme/${scheme.id}`)}
    >

      {/* Best match badge */}
      {isBestMatch && (
        <div className="absolute -top-3 left-4 z-10">
          <span className="badge bg-accent text-white text-xs px-3 py-1">
            ★ Best Match
          </span>
        </div>
      )}

      {/* ── Category image ─────────────────────────────────────── */}
      <div className="relative w-full h-44 mb-4 overflow-hidden rounded-xl">
        <img
          src={imageSrc}
          alt={scheme.category}
          className="w-full h-full object-cover"
          onError={(e) => { e.target.style.display = "none" }}
        />
        {/* Category badge on top of image */}
        <span className={`absolute top-3 left-3 badge text-xs ${colorClass}`}>
          {scheme.category}
        </span>
      </div>

      {/* Name */}
      <h3 className="text-lg font-bold text-neutral-900 mb-2 leading-snug overflow-hidden break-words">
        {scheme.name}
      </h3>

      {/* Benefit */}
      {scheme.benefits && (
        <p className="text-success font-semibold text-base mb-3 overflow-hidden break-all max-h-40">
          {scheme.benefits}
        </p>
      )}

      {/* Description */}
      <p className="text-neutral-700 text-sm leading-relaxed mb-4 overflow-hidden break-all max-h-20">
        {scheme.description}
      </p>

      {/* Eligibility tags */}
      {scheme.eligibility_criteria && (
        <div className="flex flex-wrap gap-2 mb-4">
          {scheme.eligibility_criteria.min_age && (
            <span className="text-xs bg-neutral-100 text-neutral-700 px-2 py-1 rounded-lg">
              Age: {scheme.eligibility_criteria.min_age}+
            </span>
          )}
          {scheme.eligibility_criteria.gender && (
            <span className="text-xs bg-neutral-100 text-neutral-700 px-2 py-1 rounded-lg">
              {scheme.eligibility_criteria.gender === "F" ? "Women only" : "Men only"}
            </span>
          )}
          {scheme.eligibility_criteria.max_income && (
            <span className="text-xs bg-neutral-100 text-neutral-700 px-2 py-1 rounded-lg">
              Income ≤ ₹{scheme.eligibility_criteria.max_income.toLocaleString()}
            </span>
          )}
        </div>
      )}

      {/* Action buttons */}
      <div className="flex gap-3 mt-auto">
        <button
          onClick={(e) => { e.stopPropagation(); navigate(`/scheme/${scheme.id}`) }}
          className="flex-1 btn-primary py-2 text-sm rounded-lg min-h-0"
        >
          View Details
        </button>
        {scheme.form_url && (
          <a
            href={scheme.form_url}
            target="_blank"
            rel="noreferrer"
            onClick={(e) => e.stopPropagation()}
            className="flex-1 btn-secondary py-2 text-sm rounded-lg min-h-0 text-center"
          >
            Apply Now
          </a>
        )}
      </div>
    </div>
  )
}