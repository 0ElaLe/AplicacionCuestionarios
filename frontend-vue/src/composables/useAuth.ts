/**
 * useAuth.ts — Composable de sesión global.
 * Gestiona el token JWT en localStorage y el estado del usuario logueado.
 */
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { apiService } from '../services/api.service'

const TOKEN_KEY = 'iq_token'

const token = ref<string | null>(localStorage.getItem(TOKEN_KEY))
const usuarioActual = ref<Record<string, unknown> | null>(null)

export function useAuth() {
  const router = useRouter()
  const estaAutenticado = computed(() => !!token.value)

  // ── Registro ────────────────────────────────────────────────
  async function registro(nombre: string, correo: string, password: string): Promise<string | null> {
    try {
      const data = await apiService.registro(nombre, correo, password)
      _guardarSesion(data.token, data.usuario)
      return null
    } catch (e: unknown) {
      return e instanceof Error ? e.message : 'Error en el registro'
    }
  }

  // ── Login ────────────────────────────────────────────────────
  async function login(correo: string, password: string): Promise<string | null> {
    try {
      const data = await apiService.login(correo, password)
      _guardarSesion(data.token, data.usuario)
      return null
    } catch (e: unknown) {
      return e instanceof Error ? e.message : 'Error al iniciar sesión'
    }
  }

  // ── Logout ───────────────────────────────────────────────────
  function logout() {
    localStorage.removeItem(TOKEN_KEY)
    token.value = null
    usuarioActual.value = null
    router.push('/')
  }

  // ── Cargar perfil desde token guardado ───────────────────────
  async function cargarPerfil() {
    if (!token.value) return
    try {
      const data = await apiService.meProfile()
      usuarioActual.value = data.usuario
    } catch {
      logout()
    }
  }

  function _guardarSesion(t: string, usuario: Record<string, unknown>) {
    localStorage.setItem(TOKEN_KEY, t)
    token.value = t
    usuarioActual.value = usuario
  }

  return {
    token,
    usuarioActual,
    estaAutenticado,
    registro,
    login,
    logout,
    cargarPerfil,
  }
}
