export const ROLE_LEVELS = Object.freeze({
  visitor: 0,
  publisher: 10,
  admin: 20,
  superadmin: 30,
})

export function hasMinimumRole(role, minimumRole) {
  const userLevel = ROLE_LEVELS[role]
  const requiredLevel = ROLE_LEVELS[minimumRole]
  return userLevel !== undefined && requiredLevel !== undefined && userLevel >= requiredLevel
}
