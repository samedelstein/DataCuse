export const SYRACUSE_LAT = 43.0481;
export const SYRACUSE_LNG = -76.1474;
export const MAX_ISSUE_LENGTH = 800;

export function partitionRequestTypes(requestTypes) {
  const rawTypes = Array.isArray(requestTypes) ? requestTypes : [];
  const uniqueTitles = (types) => [
    ...new Set(types.map((type) => type.title?.trim()).filter(Boolean)),
  ];

  return {
    submittable: uniqueTitles(
      rawTypes.filter((type) => type.block_submission === false),
    ),
    blocked: uniqueTitles(
      rawTypes.filter((type) => type.block_submission === true),
    ),
  };
}

export function validateRecommendation(content, submittable, blocked) {
  if (!content || typeof content !== 'object') {
    throw new Error('The recommendation was not valid JSON.');
  }

  if (content.original_intent_blocked === true) {
    if (!blocked.includes(content.blocked_category_name)) {
      throw new Error('The recommendation did not identify a verified blocked category.');
    }

    return {
      kind: 'blocked',
      blockedCategory: content.blocked_category_name,
      reasoning: content.strategy_reasoning?.trim() || '',
    };
  }

  if (!submittable.includes(content.workaround_category)) {
    throw new Error('The recommendation did not return an exact available category.');
  }

  if (!content.strategy_reasoning?.trim() || !content.draft_text?.trim()) {
    throw new Error('The recommendation was missing required guidance.');
  }

  return {
    kind: 'available',
    category: content.workaround_category,
    reasoning: content.strategy_reasoning.trim(),
    draftText: content.draft_text.trim(),
  };
}

export function getBlockedGuidance(category) {
  if (/call dispatch at 315-448-8360/i.test(category)) {
    return 'Cityline directs residents to call traffic dispatch at 315-448-8360 for this issue.';
  }

  if (/snow plow map/i.test(category)) {
    return 'Cityline directs residents to its snow plow map for this information.';
  }

  if (/sidewalk snow removal map/i.test(category)) {
    return 'Cityline directs residents to its sidewalk snow-removal page for this information.';
  }

  if (/OCRRA/i.test(category)) {
    return 'Cityline directs residents to OCRRA for electronic or hazardous-waste disposal.';
  }

  return 'This category is not currently accepting an online submission at the central Syracuse location. Open Cityline to review its latest instructions or contact Cityline directly.';
}
