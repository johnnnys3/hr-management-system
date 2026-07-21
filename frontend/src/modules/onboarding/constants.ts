import type { OnboardingTaskStatus } from '../../api/types'

export const TASK_STATUS_COLORS: Record<OnboardingTaskStatus, string> = {
  pending: 'default',
  in_progress: 'gold',
  completed: 'green',
  skipped: 'red',
}
