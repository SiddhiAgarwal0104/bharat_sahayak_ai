// src/components/ui/SchemeCard.jsx
import { useNavigate } from "react-router-dom"

const CATEGORY_COLORS = {
  education:   "bg-blue-100 text-blue-800",
  agriculture: "bg-green-100 text-green-800",
  health:      "bg-red-100 text-red-800",
  pension:     "bg-amber-100 text-amber-800",
  other:       "bg-gray-100 text-gray-700",
}

export default function SchemeCard({ scheme, isBestMatch = false }) {
  const navigate = useNavigate()
  const colorClass = CATEGORY_COLORS[scheme.category] || CATEGORY_COLORS.other

  return (
    <div className={`card relative hover:shadow-md transition-shadow cursor-pointer
                     ${isBestMatch ? "border-2 border-accent" : ""}`}
         onClick={() => navigate(`/scheme/${scheme.id}`)}>

      {/* Best match badge */}
      {isBestMatch && (
        <div className="absolute -top-3 left-4">
          <span className="badge bg-accent text-white text-xs px-3 py-1">
            ★ Best Match
          </span>
        </div>
      )}

      {/* Category */}
      <span className={`badge text-xs mb-3 ${colorClass}`}>
        {scheme.category}
      </span>

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
          className="flex-1 btn-primary py-2 text-sm rounded-lg min-h-0">
          View Details
        </button>
        {scheme.form_url && (
          <a href={scheme.form_url} target="_blank" rel="noreferrer"
             onClick={(e) => e.stopPropagation()}
             className="flex-1 btn-secondary py-2 text-sm rounded-lg min-h-0 text-center">
            Apply Now
          </a>
        )}
      </div>
    </div>
  )
}