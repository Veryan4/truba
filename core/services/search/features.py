from shared.types import story_types, feature_types


def extract_solr_features(string: str) -> feature_types.SolrFeatures:
  """Converts the string of features returned from Solr to typed object.

    Args:
        string: represents the [features] property returned by Solr.

    Returns:
        The mapped features typed as SolrFeatures.
    """

  arr = string.split(',')
  dic = {str(item.split('=')[0]): float(item.split('=')[1]) for item in arr}
  features = feature_types.SolrFeatures(**dic)
  return features


def extract_ranking_features(
    story: story_types.Story) -> feature_types.RankingFeatures:
  """Extracts features used for tensor flow recommendations.

    Args:
        story: Story from which to extract features.

    Returns:
        The extreacted RankingFeatures.
    """

  ranking_features = feature_types.RankingFeatures()
  if story.title:
    ranking_features.story_title = story.title
  if story.source and story.source.rank_in_alexa:
    ranking_features.source_alexa_rank = story.source.rank_in_alexa
  if story.read_count:
    ranking_features.read_count = story.read_count
  if story.shared_count:
    ranking_features.shared_count = story.shared_count
  if story.angry_count:
    ranking_features.angry_count = story.angry_count
  if story.cry_count:
    ranking_features.cry_count = story.cry_count
  if story.neutral_count:
    ranking_features.neutral_count = story.neutral_count
  if story.smile_count:
    ranking_features.smile_count = story.smile_count
  if story.happy_count:
    ranking_features.happy_count = story.happy_count
  if story.source:
    ranking_features.source_id = str(story.source.source_id)
  if story.author:
    ranking_features.author_id = str(story.author.author_id)
  if story.keywords:
    most_frequent_keyword = max(story.keywords,
                                key=lambda word: word.frequency)
    if most_frequent_keyword and most_frequent_keyword.keyword.text:
      ranking_features.most_frequent_keyword = most_frequent_keyword.keyword.text
  if story.entities:
    most_frequent_entity = max(story.entities, key=lambda ent: ent.frequency)
    if most_frequent_entity and most_frequent_entity.entity.links:
      ranking_features.most_frequent_entity = most_frequent_entity.entity.links
  return ranking_features
