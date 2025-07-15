package controllers

import (
	"context"
	"strings"
	"time"

	"core/internal/feedback"
	"core/internal/story"
	"core/internal/user"

	"github.com/google/uuid"
	"github.com/mark3labs/mcp-go/mcp"
	"github.com/mark3labs/mcp-go/server"
)

func McpTools(server *server.MCPServer) *server.MCPServer {

	// Stories
	storyUri := "story://specific/{storyId}"
	storyByIdTemplate := mcp.NewResourceTemplate(
		storyUri,
		"Specific Story",
		mcp.WithTemplateDescription("Returns a specific story when Id is provided"),
		mcp.WithTemplateMIMEType("application/json"),
	)
	server.AddResourceTemplate(storyByIdTemplate, func(ctx context.Context, request mcp.ReadResourceRequest) ([]mcp.ResourceContents, error) {
		strArr := strings.Split(request.Params.URI, "/")
		storyId := strArr[3]
		story, err := story.GetStoryById(storyId)
		if err != nil {
			return nil, err
		}
		return McpResourceResponseWithJSON(request.Params.URI, story)
	})
	storyTool := mcp.NewTool("story",
		mcp.WithDescription("Returns a specific story when Id is provided"),
		mcp.WithString("storyId", mcp.Required(), mcp.Description("The ID of the story you are fetching")),
	)
	server.AddTool(storyTool, func(ctx context.Context, request mcp.CallToolRequest) (*mcp.CallToolResult, error) {
		storyId, err := request.RequireString("storyId")
		if err != nil {
			return mcp.NewToolResultError(err.Error()), nil
		}
		story, err := story.GetStoryById(storyId)
		if err != nil {
			return mcp.NewToolResultError(err.Error()), nil
		}
		uri := storyUri
		uri = strings.Replace(uri, "{storyId}", storyId, -1)
		return McpToolResponseWithJSON("the story requested", uri, story)
	})

	publicStoriesUri := "stories://public/{language}"
	publicStoriesTemplate := mcp.NewResourceTemplate(
		publicStoriesUri,
		"Public Stories",
		mcp.WithTemplateDescription("Returns latest stories of the day. One story per source."),
		mcp.WithTemplateMIMEType("application/json"),
	)
	server.AddResourceTemplate(publicStoriesTemplate, func(ctx context.Context, request mcp.ReadResourceRequest) ([]mcp.ResourceContents, error) {
		strArr := strings.Split(request.Params.URI, "/")
		language := strArr[3]

		stories, err := story.GetPublicStories(language)
		if err != nil {
			return nil, err
		}
		return McpResourceResponseWithJSON(request.Params.URI, stories)
	})

	publicStoriesTool := mcp.NewTool("publicStories",
		mcp.WithDescription("Returns latest stories of the day. One story per source."),
		mcp.WithString("language", mcp.Required(), mcp.Description("Which language are the stories written in.")),
	)
	server.AddTool(publicStoriesTool, func(ctx context.Context, request mcp.CallToolRequest) (*mcp.CallToolResult, error) {
		language, err := request.RequireString("language")
		if err != nil {
			return mcp.NewToolResultError(err.Error()), nil
		}
		publicStories, err := story.GetPublicStories(language)
		if err != nil {
			return mcp.NewToolResultError(err.Error()), nil
		}
		uri := publicStoriesUri
		uri = strings.Replace(uri, "{language}", language, -1)
		return McpToolResponseWithJSON("the latest stories of the day", uri, publicStories)
	})

	recommendedStoriesUri := "stories://recommended/{language}/{userId}"
	recommendedStoriesTemplate := mcp.NewResourceTemplate(
		recommendedStoriesUri,
		"Recommended Stories",
		mcp.WithTemplateDescription("Returns latest stories of the day which are based on the user preferences. One story per source."),
		mcp.WithTemplateMIMEType("application/json"),
	)
	server.AddResourceTemplate(recommendedStoriesTemplate, func(ctx context.Context, request mcp.ReadResourceRequest) ([]mcp.ResourceContents, error) {
		strArr := strings.Split(request.Params.URI, "/")
		language := strArr[3]
		userId := strArr[4]
		stories, err := story.GetRecommendedStories(userId, language)
		if err != nil {
			return nil, err
		}
		return McpResourceResponseWithJSON(request.Params.URI, stories)
	})

	recommendedStoriesTool := mcp.NewTool("recommendedStories",
		mcp.WithDescription("Get recent stories which match the users preferences"),
		mcp.WithString("userId", mcp.Required(), mcp.Description("The ID of the user")),
		mcp.WithString("language", mcp.Required(), mcp.Description("Which language are the stories written in.")),
	)
	server.AddTool(recommendedStoriesTool, func(ctx context.Context, request mcp.CallToolRequest) (*mcp.CallToolResult, error) {
		userId, err := request.RequireString("userId")
		if err != nil {
			return mcp.NewToolResultError(err.Error()), nil
		}
		language, err := request.RequireString("language")
		if err != nil {
			return mcp.NewToolResultError(err.Error()), nil
		}
		recommendedStories, err := user.GetFavorites(userId, user.FAVORITE_SOURCE_DB_COLLECTION_NAME, 20, language)
		if err != nil {
			return mcp.NewToolResultError(err.Error()), nil
		}
		uri := recommendedStoriesUri
		uri = strings.Replace(uri, "{userId}", userId, -1)
		uri = strings.Replace(uri, "{language}", language, -1)
		return McpToolResponseWithJSON("Recent stories which match the users preferences", uri, recommendedStories)
	})

	// Favorites
	favoriteSourcesUri := "user://favorites/sources/{userId}/{language}"
	favoriteSourcesTemplate := mcp.NewResourceTemplate(
		favoriteSourcesUri,
		"Public Stories",
		mcp.WithTemplateDescription("Get a user's feedback list given the user's Id in order of most favorite to least favorite"),
		mcp.WithTemplateMIMEType("application/json"),
	)
	server.AddResourceTemplate(favoriteSourcesTemplate, func(ctx context.Context, request mcp.ReadResourceRequest) ([]mcp.ResourceContents, error) {
		strArr := strings.Split(request.Params.URI, "/")
		userId := strArr[4]
		language := strArr[5]

		favorites, err := user.GetFavorites(userId, user.FAVORITE_SOURCE_DB_COLLECTION_NAME, 20, language)
		if err != nil {
			return nil, err
		}
		return McpResourceResponseWithJSON(request.Params.URI, favorites)
	})

	favoriteSourcesTool := mcp.NewTool("favoriteSources",
		mcp.WithDescription("Get a user's favorite Sources"),
		mcp.WithString("userId", mcp.Required(), mcp.Description("The ID of the user")),
		mcp.WithString("language", mcp.Required(), mcp.Description("Which language does the source publish in")),
	)
	server.AddTool(favoriteSourcesTool, func(ctx context.Context, request mcp.CallToolRequest) (*mcp.CallToolResult, error) {
		userId, err := request.RequireString("userId")
		if err != nil {
			return mcp.NewToolResultError(err.Error()), nil
		}
		language, err := request.RequireString("language")
		if err != nil {
			return mcp.NewToolResultError(err.Error()), nil
		}
		favorites, err := user.GetFavorites(userId, user.FAVORITE_SOURCE_DB_COLLECTION_NAME, 20, language)
		if err != nil {
			return mcp.NewToolResultError(err.Error()), nil
		}
		uri := favoriteSourcesUri
		uri = strings.Replace(uri, "{userId}", userId, -1)
		uri = strings.Replace(uri, "{language}", language, -1)
		return McpToolResponseWithJSON("the user's favorite sources", uri, favorites)
	})

	// User Feedback
	feedbackListUri := "feedback://user/{userId}"
	feedbackListTemplate := mcp.NewResourceTemplate(
		feedbackListUri,
		"List of feedback provided by the user",
		mcp.WithTemplateDescription("Get a user's feedback list given the user's Id"),
		mcp.WithTemplateMIMEType("application/json"),
	)
	server.AddResourceTemplate(feedbackListTemplate, func(ctx context.Context, request mcp.ReadResourceRequest) ([]mcp.ResourceContents, error) {
		strArr := strings.Split(request.Params.URI, "/")
		userId := strArr[3]
		feedbackList, err := feedback.GetFeedbackList(userId)
		if err != nil {
			return nil, err
		}
		return McpResourceResponseWithJSON(request.Params.URI, feedbackList)
	})

	feedbackListTool := mcp.NewTool("feedbackList",
		mcp.WithDescription("Get a list of previous feedback collected from the user"),
		mcp.WithString("userId", mcp.Required(), mcp.Description("The ID of the user")),
	)
	server.AddTool(feedbackListTool, func(ctx context.Context, request mcp.CallToolRequest) (*mcp.CallToolResult, error) {
		userId, err := request.RequireString("userId")
		if err != nil {
			return mcp.NewToolResultError(err.Error()), nil
		}
		feedbackList, err := feedback.GetFeedbackList(userId)
		if err != nil {
			return mcp.NewToolResultError(err.Error()), nil
		}
		uri := feedbackListUri
		uri = strings.Replace(uri, "{userId}", userId, -1)
		return McpToolResponseWithJSON("The user's list of previous feedback", uri, feedbackList)
	})

	feedbackReceivedTool := mcp.NewTool("feedbackReceived",
		mcp.WithDescription("Submit user feedback"),
		mcp.WithString("userId", mcp.Required(), mcp.Description("The ID of the user submitting feedback")),
		mcp.WithString("storyId", mcp.Required(), mcp.Description("The ID of the story the feedback is for")),
		mcp.WithString("feedbackType", mcp.Required(), mcp.Description("The type of feedback. One of the following values; read, shared, angry, cry, neutral, smile, happy")),
	)
	server.AddTool(feedbackReceivedTool, func(ctx context.Context, request mcp.CallToolRequest) (*mcp.CallToolResult, error) {
		userId, err := request.RequireString("userId")
		if err != nil {
			return mcp.NewToolResultError(err.Error()), nil
		}
		storyId, err := request.RequireString("storyId")
		if err != nil {
			return mcp.NewToolResultError(err.Error()), nil
		}
		feedbackType, err := request.RequireString("feedbackType")
		if err != nil {
			return mcp.NewToolResultError(err.Error()), nil
		}
		userFeedback := feedback.UserFeedback{
			UserId:           userId,
			StoryId:          storyId,
			FeedbackDatetime: time.Now(),
			FeedbackType:     feedback.FeedbackType(feedbackType),
		}
		if err := feedback.FeedbackReceived(userFeedback); err != nil {
			return mcp.NewToolResultError(err.Error()), nil
		}
		return mcp.NewToolResultText("Feedback received"), nil
	})

	allSourcesUri := "sources://all/{language}"
	allSourcesTemplate := mcp.NewResourceTemplate(
		allSourcesUri,
		"All Sources",
		mcp.WithTemplateDescription("Returns all sources for a given language"),
		mcp.WithTemplateMIMEType("application/json"),
	)
	server.AddResourceTemplate(allSourcesTemplate, func(ctx context.Context, request mcp.ReadResourceRequest) ([]mcp.ResourceContents, error) {
		strArr := strings.Split(request.Params.URI, "/")
		language := strArr[3]
		sources, err := story.GetAllSources(language)
		if err != nil {
			return nil, err
		}
		return McpResourceResponseWithJSON(request.Params.URI, sources)
	})

	allSourcesTool := mcp.NewTool("allSources",
		mcp.WithDescription("Returns all sources for a given language"),
		mcp.WithString("language", mcp.Required(), mcp.Description("Which language do the sources publish in")),
	)
	server.AddTool(allSourcesTool, func(ctx context.Context, request mcp.CallToolRequest) (*mcp.CallToolResult, error) {
		language, err := request.RequireString("language")
		if err != nil {
			return mcp.NewToolResultError(err.Error()), nil
		}
		sources, err := story.GetAllSources(language)
		if err != nil {
			return mcp.NewToolResultError(err.Error()), nil
		}
		uri := allSourcesUri
		uri = strings.Replace(uri, "{language}", language, -1)
		return McpToolResponseWithJSON("all sources for the given language", uri, sources)
	})

	authorByNameUri := "author://by-name/{name}"
	authorByNameTemplate := mcp.NewResourceTemplate(
		authorByNameUri,
		"Author By Name",
		mcp.WithTemplateDescription("Returns an author for a given name"),
		mcp.WithTemplateMIMEType("application/json"),
	)
	server.AddResourceTemplate(authorByNameTemplate, func(ctx context.Context, request mcp.ReadResourceRequest) ([]mcp.ResourceContents, error) {
		strArr := strings.Split(request.Params.URI, "/")
		name := strArr[3]
		author, err := story.GetAuthorByName(name)
		if err != nil {
			return nil, err
		}
		return McpResourceResponseWithJSON(request.Params.URI, author)
	})

	authorByNameTool := mcp.NewTool("authorByName",
		mcp.WithDescription("Returns an author for a given name"),
		mcp.WithString("name", mcp.Required(), mcp.Description("The name of the author")),
	)
	server.AddTool(authorByNameTool, func(ctx context.Context, request mcp.CallToolRequest) (*mcp.CallToolResult, error) {
		name, err := request.RequireString("name")
		if err != nil {
			return mcp.NewToolResultError(err.Error()), nil
		}
		author, err := story.GetAuthorByName(name)
		if err != nil {
			return mcp.NewToolResultError(err.Error()), nil
		}
		uri := authorByNameUri
		uri = strings.Replace(uri, "{name}", name, -1)
		return McpToolResponseWithJSON("the author for the given name", uri, author)
	})

	entitiesByLinksUri := "entity://specific/{links}"
	entitiesByLinksTemplate := mcp.NewResourceTemplate(
		entitiesByLinksUri,
		"Entities By Links",
		mcp.WithTemplateDescription("Returns entities for a given list of links"),
		mcp.WithTemplateMIMEType("application/json"),
	)
	server.AddResourceTemplate(entitiesByLinksTemplate, func(ctx context.Context, request mcp.ReadResourceRequest) ([]mcp.ResourceContents, error) {
		strArr := strings.Split(request.Params.URI, "/")
		links := strArr[3]
		entities, err := story.GetEntitiesByLinks(strings.Split(links, ","))
		if err != nil {
			return nil, err
		}
		return McpResourceResponseWithJSON(request.Params.URI, entities)
	})

	entitiesByLinksTool := mcp.NewTool("entitiesByLinks",
		mcp.WithDescription("Returns entities for a given list of links"),
		mcp.WithString("links", mcp.Required(), mcp.Description("A comma-separated list of links")),
	)
	server.AddTool(entitiesByLinksTool, func(ctx context.Context, request mcp.CallToolRequest) (*mcp.CallToolResult, error) {
		links, err := request.RequireString("links")
		if err != nil {
			return mcp.NewToolResultError(err.Error()), nil
		}
		entities, err := story.GetEntitiesByLinks(strings.Split(links, ","))
		if err != nil {
			return mcp.NewToolResultError(err.Error()), nil
		}
		return McpToolResponseWithJSON("the entities for the given links", entitiesByLinksUri, entities)
	})

	keywordsByTextsUri := "keyword://specific/{texts}/{language}"
	keywordsByTextsTemplate := mcp.NewResourceTemplate(
		keywordsByTextsUri,
		"Keywords By Texts",
		mcp.WithTemplateDescription("Returns keywords for a given list of texts"),
		mcp.WithTemplateMIMEType("application/json"),
	)
	server.AddResourceTemplate(keywordsByTextsTemplate, func(ctx context.Context, request mcp.ReadResourceRequest) ([]mcp.ResourceContents, error) {
		strArr := strings.Split(request.Params.URI, "/")
		texts := strArr[3]
		language := strArr[4]
		keywords, err := story.GetKeywordsByTexts(strings.Split(texts, ","), language)
		if err != nil {
			return nil, err
		}
		return McpResourceResponseWithJSON(request.Params.URI, keywords)
	})

	keywordsByTextsTool := mcp.NewTool("keywordsByTexts",
		mcp.WithDescription("Returns keywords for a given list of texts"),
		mcp.WithString("texts", mcp.Required(), mcp.Description("A comma-separated list of texts")),
		mcp.WithString("language", mcp.Required(), mcp.Description("The language of the keywords")),
	)
	server.AddTool(keywordsByTextsTool, func(ctx context.Context, request mcp.CallToolRequest) (*mcp.CallToolResult, error) {
		texts, err := request.RequireString("texts")
		if err != nil {
			return mcp.NewToolResultError(err.Error()), nil
		}
		language, err := request.RequireString("language")
		if err != nil {
			return mcp.NewToolResultError(err.Error()), nil
		}
		keywords, err := story.GetKeywordsByTexts(strings.Split(texts, ","), language)
		if err != nil {
			return mcp.NewToolResultError(err.Error()), nil
		}
		return McpToolResponseWithJSON("the keywords for the given texts", keywordsByTextsUri, keywords)
	})

	updateSourceReputationTool := mcp.NewTool("updateSourceReputation",
		mcp.WithDescription("Updates the reputation of a source"),
		mcp.WithString("sourceId", mcp.Required(), mcp.Description("The ID of the source to update")),
		mcp.WithNumber("reward", mcp.Required(), mcp.Description("The reward to apply to the source's reputation")),
	)
	server.AddTool(updateSourceReputationTool, func(ctx context.Context, request mcp.CallToolRequest) (*mcp.CallToolResult, error) {
		sourceId, err := request.RequireString("sourceId")
		if err != nil {
			return mcp.NewToolResultError(err.Error()), nil
		}
		reward, err := request.RequireFloat("reward")
		if err != nil {
			return mcp.NewToolResultError(err.Error()), nil
		}
		if err := story.UpdateSourceReputation(sourceId, float32(reward)); err != nil {
			return mcp.NewToolResultError(err.Error()), nil
		}
		return mcp.NewToolResultText("Source reputation updated"), nil
	})

	updateFavoriteFromStoryTool := mcp.NewTool("updateFavoriteFromStory",
		mcp.WithDescription("Updates a user's favorite status for a story"),
		mcp.WithString("userId", mcp.Required(), mcp.Description("The ID of the user")),
		mcp.WithString("identifier", mcp.Required(), mcp.Description("The identifier of the item to update")),
		mcp.WithString("value", mcp.Required(), mcp.Description("The new value of the favorite item")),
		mcp.WithNumber("reward", mcp.Required(), mcp.Description("The reward to apply")),
		mcp.WithString("dbCollection", mcp.Required(), mcp.Description("The database collection")),
		mcp.WithString("language", mcp.Required(), mcp.Description("The language of the story")),
	)
	server.AddTool(updateFavoriteFromStoryTool, func(ctx context.Context, request mcp.CallToolRequest) (*mcp.CallToolResult, error) {
		userId, err := request.RequireString("userId")
		if err != nil {
			return mcp.NewToolResultError(err.Error()), nil
		}
		identifier, err := request.RequireString("identifier")
		if err != nil {
			return mcp.NewToolResultError(err.Error()), nil
		}
		value, err := request.RequireString("value")
		if err != nil {
			return mcp.NewToolResultError(err.Error()), nil
		}
		reward, err := request.RequireFloat("reward")
		if err != nil {
			return mcp.NewToolResultError(err.Error()), nil
		}
		dbCollection, err := request.RequireString("dbCollection")
		if err != nil {
			return mcp.NewToolResultError(err.Error()), nil
		}
		language, err := request.RequireString("language")
		if err != nil {
			return mcp.NewToolResultError(err.Error()), nil
		}
		if err := user.UpdateFavoriteFromStory(userId, identifier, value, float32(reward), dbCollection, language); err != nil {
			return mcp.NewToolResultError(err.Error()), nil
		}
		return mcp.NewToolResultText("Favorite updated from story"), nil
	})

	getPersonalizationUri := "user://personalization/{userId}/{language}"
	getPersonalizationTemplate := mcp.NewResourceTemplate(
		getPersonalizationUri,
		"Personalization",
		mcp.WithTemplateDescription("Returns a user's personalization profile"),
		mcp.WithTemplateMIMEType("application/json"),
	)
	server.AddResourceTemplate(getPersonalizationTemplate, func(ctx context.Context, request mcp.ReadResourceRequest) ([]mcp.ResourceContents, error) {
		strArr := strings.Split(request.Params.URI, "/")
		userId := strArr[3]
		language := strArr[4]
		personalization, err := user.GetPersonalization(userId, language)
		if err != nil {
			return nil, err
		}
		return McpResourceResponseWithJSON(request.Params.URI, personalization)
	})

	getPersonalizationTool := mcp.NewTool("getPersonalization",
		mcp.WithDescription("Returns a user's personalization profile"),
		mcp.WithString("userId", mcp.Required(), mcp.Description("The ID of the user")),
		mcp.WithString("language", mcp.Required(), mcp.Description("The language of the personalization")),
	)
	server.AddTool(getPersonalizationTool, func(ctx context.Context, request mcp.CallToolRequest) (*mcp.CallToolResult, error) {
		userId, err := request.RequireString("userId")
		if err != nil {
			return mcp.NewToolResultError(err.Error()), nil
		}
		language, err := request.RequireString("language")
		if err != nil {
			return mcp.NewToolResultError(err.Error()), nil
		}
		personalization, err := user.GetPersonalization(userId, language)
		if err != nil {
			return mcp.NewToolResultError(err.Error()), nil
		}
		uri := getPersonalizationUri
		uri = strings.Replace(uri, "{userId}", userId, -1)
		uri = strings.Replace(uri, "{language}", language, -1)
		return McpToolResponseWithJSON("the user's personalization profile", uri, personalization)
	})

	addReadStoryTool := mcp.NewTool("addReadStory",
		mcp.WithDescription("Marks a story as read by a user"),
		mcp.WithString("userId", mcp.Required(), mcp.Description("The ID of the user")),
		mcp.WithString("storyId", mcp.Required(), mcp.Description("The ID of the story")),
	)
	server.AddTool(addReadStoryTool, func(ctx context.Context, request mcp.CallToolRequest) (*mcp.CallToolResult, error) {
		userId, err := request.RequireString("userId")
		if err != nil {
			return mcp.NewToolResultError(err.Error()), nil
		}
		storyId, err := request.RequireString("storyId")
		if err != nil {
			return mcp.NewToolResultError(err.Error()), nil
		}
		readStory := user.ReadStory{
			UserId:   userId,
			StoryId:  storyId,
			ReadTime: time.Now(),
		}
		if err := user.AddReadStory(readStory); err != nil {
			return mcp.NewToolResultError(err.Error()), nil
		}
		return mcp.NewToolResultText("Story marked as read"), nil
	})

	getReadStoryIdsUri := "user://read-story-ids/{userId}"
	getReadStoryIdsTemplate := mcp.NewResourceTemplate(
		getReadStoryIdsUri,
		"Read Story IDs",
		mcp.WithTemplateDescription("Returns the IDs of stories a user has read"),
		mcp.WithTemplateMIMEType("application/json"),
	)
	server.AddResourceTemplate(getReadStoryIdsTemplate, func(ctx context.Context, request mcp.ReadResourceRequest) ([]mcp.ResourceContents, error) {
		strArr := strings.Split(request.Params.URI, "/")
		userId := strArr[3]
		readStoryIds, err := user.GetReadStoryIds(userId)
		if err != nil {
			return nil, err
		}
		return McpResourceResponseWithJSON(request.Params.URI, readStoryIds)
	})

	getReadStoryIdsTool := mcp.NewTool("getReadStoryIds",
		mcp.WithDescription("Returns the IDs of stories a user has read"),
		mcp.WithString("userId", mcp.Required(), mcp.Description("The ID of the user")),
	)
	server.AddTool(getReadStoryIdsTool, func(ctx context.Context, request mcp.CallToolRequest) (*mcp.CallToolResult, error) {
		userId, err := request.RequireString("userId")
		if err != nil {
			return mcp.NewToolResultError(err.Error()), nil
		}
		readStoryIds, err := user.GetReadStoryIds(userId)
		if err != nil {
			return mcp.NewToolResultError(err.Error()), nil
		}
		uri := getReadStoryIdsUri
		uri = strings.Replace(uri, "{userId}", userId, -1)
		return McpToolResponseWithJSON("the IDs of stories the user has read", uri, readStoryIds)
	})

	authorsByIdsUri := "author://multiple/{ids}"
	authorsByIdsTemplate := mcp.NewResourceTemplate(
		authorsByIdsUri,
		"Authors By IDs",
		mcp.WithTemplateDescription("Returns authors for a given list of IDs"),
		mcp.WithTemplateMIMEType("application/json"),
	)
	server.AddResourceTemplate(authorsByIdsTemplate, func(ctx context.Context, request mcp.ReadResourceRequest) ([]mcp.ResourceContents, error) {
		strArr := strings.Split(request.Params.URI, "/")
		authorIdsString := strArr[3]
		authorIds := strings.Split(authorIdsString, ",")
		aIds := make([]uuid.UUID, len(authorIds))
		for _, authorId := range authorIds {
			aid, er := uuid.Parse(authorId)
			if er != nil {
				return nil, er
			}
			aIds = append(aIds, aid)
		}
		authors, err := story.GetAuthorsByIds(aIds)
		if err != nil {
			return nil, err
		}
		return McpResourceResponseWithJSON(request.Params.URI, authors)
	})

	authorsByIdsTool := mcp.NewTool("authorsByIds",
		mcp.WithDescription("Returns authors for a given list of IDs"),
		mcp.WithString("authorIds", mcp.Required(), mcp.Description("A comma-separated list of author IDs")),
	)
	server.AddTool(authorsByIdsTool, func(ctx context.Context, request mcp.CallToolRequest) (*mcp.CallToolResult, error) {
		authorIdsString, err := request.RequireString("authorIds")
		if err != nil {
			return mcp.NewToolResultError(err.Error()), nil
		}
		authorIds := strings.Split(authorIdsString, ",")
		aIds := make([]uuid.UUID, len(authorIds))
		for _, authorId := range authorIds {
			aid, er := uuid.Parse(authorId)
			if er != nil {
				return mcp.NewToolResultError(er.Error()), nil
			}
			aIds = append(aIds, aid)
		}
		authors, err := story.GetAuthorsByIds(aIds)
		if err != nil {
			return mcp.NewToolResultError(err.Error()), nil
		}
		return McpToolResponseWithJSON("the authors for the given IDs", authorsByIdsUri, authors)
	})

	sourceByNameUri := "source://by-name/{name}"
	sourceByNameTemplate := mcp.NewResourceTemplate(
		sourceByNameUri,
		"Source By Name",
		mcp.WithTemplateDescription("Returns a source for a given name"),
		mcp.WithTemplateMIMEType("application/json"),
	)
	server.AddResourceTemplate(sourceByNameTemplate, func(ctx context.Context, request mcp.ReadResourceRequest) ([]mcp.ResourceContents, error) {
		strArr := strings.Split(request.Params.URI, "/")
		name := strArr[3]

		source, err := story.GetSourceByName(name)
		if err != nil {
			return nil, err
		}
		return McpResourceResponseWithJSON(request.Params.URI, source)
	})

	sourceByNameTool := mcp.NewTool("sourceByName",
		mcp.WithDescription("Returns a source for a given name"),
		mcp.WithString("name", mcp.Required(), mcp.Description("The name of the source")),
	)
	server.AddTool(sourceByNameTool, func(ctx context.Context, request mcp.CallToolRequest) (*mcp.CallToolResult, error) {
		name, err := request.RequireString("name")
		if err != nil {
			return mcp.NewToolResultError(err.Error()), nil
		}
		source, err := story.GetSourceByName(name)
		if err != nil {
			return mcp.NewToolResultError(err.Error()), nil
		}
		uri := sourceByNameUri
		uri = strings.Replace(uri, "{name}", name, -1)
		return McpToolResponseWithJSON("the source for the given name", uri, source)
	})

	sourcesByIdsUri := "source://multiple/{ids}"
	sourcesByIdsTemplate := mcp.NewResourceTemplate(
		sourcesByIdsUri,
		"Sources By IDs",
		mcp.WithTemplateDescription("Returns sources for a given list of IDs"),
		mcp.WithTemplateMIMEType("application/json"),
	)
	server.AddResourceTemplate(sourcesByIdsTemplate, func(ctx context.Context, request mcp.ReadResourceRequest) ([]mcp.ResourceContents, error) {
		strArr := strings.Split(request.Params.URI, "/")
		sourceIds := strArr[3]
		sources, err := story.GetSourcesByIds(strings.Split(sourceIds, ","))
		if err != nil {
			return nil, err
		}
		return McpResourceResponseWithJSON(request.Params.URI, sources)
	})

	sourcesByIdsTool := mcp.NewTool("sourcesByIds",
		mcp.WithDescription("Returns sources for a given list of IDs"),
		mcp.WithString("sourceIds", mcp.Required(), mcp.Description("A comma-separated list of source IDs")),
	)
	server.AddTool(sourcesByIdsTool, func(ctx context.Context, request mcp.CallToolRequest) (*mcp.CallToolResult, error) {
		sourceIds, err := request.RequireString("sourceIds")
		if err != nil {
			return mcp.NewToolResultError(err.Error()), nil
		}
		sources, err := story.GetSourcesByIds(strings.Split(sourceIds, ","))
		if err != nil {
			return mcp.NewToolResultError(err.Error()), nil
		}

		return McpToolResponseWithJSON("the sources for the given IDs", sourcesByIdsUri, sources)
	})

	updateAuthorReputationTool := mcp.NewTool("updateAuthorReputation",
		mcp.WithDescription("Updates the reputation of an author"),
		mcp.WithString("authorId", mcp.Required(), mcp.Description("The ID of the author to update")),
		mcp.WithNumber("reward", mcp.Required(), mcp.Description("The reward to apply to the author's reputation")),
	)
	server.AddTool(updateAuthorReputationTool, func(ctx context.Context, request mcp.CallToolRequest) (*mcp.CallToolResult, error) {
		authorId, err := request.RequireString("authorId")
		if err != nil {
			return mcp.NewToolResultError(err.Error()), nil
		}
		reward, err := request.RequireFloat("reward")
		if err != nil {
			return mcp.NewToolResultError(err.Error()), nil
		}
		aid, er := uuid.Parse(authorId)
		if er != nil {
			return mcp.NewToolResultError(er.Error()), nil
		}

		if err := story.UpdateAuthorReputation(aid, float32(reward)); err != nil {
			return mcp.NewToolResultError(err.Error()), nil
		}
		return mcp.NewToolResultText("Author reputation updated"), nil
	})

	return server
}
