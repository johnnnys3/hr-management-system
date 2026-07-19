export interface Me {
  id: number
  email: string
  groups: string[]
  second_factor_enrollment_pending: boolean
}

export interface LoginSuccess {
  id: number
  email: string
  groups: string[]
  second_factor_enrollment_required?: boolean
}

export interface LoginSecondFactorRequired {
  second_factor_required: true
}

export type LoginResponse = LoginSuccess | LoginSecondFactorRequired

export function isSecondFactorRequired(response: LoginResponse): response is LoginSecondFactorRequired {
  return 'second_factor_required' in response
}

export interface UserAccount {
  id: number
  email: string
  is_active: boolean
  groups: string[]
  created_at: string
  updated_at: string
}

export interface SecondFactorEnrollResponse {
  provisioning_uri: string
}

export interface SecondFactorRecoveryRequestRecord {
  id: number
  status: 'pending' | 'approved' | 'denied'
  requested_at: string
  decided_at: string | null
}

export interface Department {
  id: number
  name: string
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface JobTitle {
  id: number
  name: string
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface RoleGrantRequestRecord {
  id: number
  requester: number
  subject: number
  role: number
  status: 'pending' | 'approved' | 'refused'
  approver: number | null
  requested_at: string
  decided_at: string | null
}
