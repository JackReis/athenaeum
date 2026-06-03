/**
 * Canonical category taxonomy for the athenaeum marketplace.
 * Single source of truth for category lists, icons, and color mappings.
 */

export const categories = [
  'automation',
  'business-tools',
  'devops',
  'code-analysis',
  'debugging',
  'ai-ml-assistance',
  'frontend-development',
  'security',
  'testing',
  'documentation',
  'performance',
  'database',
  'cloud-infrastructure',
  'accessibility',
  'mobile',
  'skill-enhancers',
  'other',
] as const;

export type Category = (typeof categories)[number];

export const categoryIcons: Record<Category, string> = {
  automation: '⚙️',
  'business-tools': '💼',
  devops: '🚀',
  'code-analysis': '🔍',
  debugging: '🐛',
  'ai-ml-assistance': '🤖',
  'frontend-development': '🎨',
  security: '🔒',
  testing: '✅',
  documentation: '📚',
  performance: '⚡',
  database: '💾',
  'cloud-infrastructure': '☁️',
  accessibility: '♿',
  mobile: '📱',
  'skill-enhancers': '📦',
  other: '🔧',
};

export const categoryColors: Record<Category, string> = {
  automation: 'category-purple',
  'business-tools': 'category-blue',
  devops: 'category-green',
  'code-analysis': 'category-cyan',
  debugging: 'category-red',
  'ai-ml-assistance': 'category-pink',
  'frontend-development': 'category-indigo',
  security: 'category-orange',
  testing: 'category-teal',
  documentation: 'category-gray',
  performance: 'category-yellow',
  database: 'category-violet',
  'cloud-infrastructure': 'category-sky',
  accessibility: 'category-lime',
  mobile: 'category-fuchsia',
  'skill-enhancers': 'category-emerald',
  other: 'category-neutral',
};
