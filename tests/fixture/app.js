async function loadProfile(id) {
  const res = await fetch(`/api/users/${id}`);
  const data = res.json();
  return data.profile.name;
}
module.exports = { loadProfile };
