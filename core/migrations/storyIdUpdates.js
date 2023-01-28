const storiesBatchSize = 10000
let storiesBatch = []

const storiesCursor = db.Story.find({})

while (storiesCursor.hasNext()) {
    const story = storiesCursor.next()

    const storyUpdate = {
        updateOne : {
            filter: { _id: story._id},
            update: {
                $set: {
                    author_id: story.author.author_id,
                    source_id: story.source.source_id,
                    entity_links: story.entities.map(ent => ent.links)
                },
                $unset: {
                    author: null,
                    source: null,
                    entities: null
                }
            }
        }
    }

    storiesBatch.push(storyUpdate)

    if (storiesBatch.length === storiesBatchSize){
        console.log(`Updating ${storiesBatch.length} stories`) 
        db.Story.bulkWrite(storiesBatch)
        storiesBatch = []
    }
}

if (storiesBatch.length > 0){
    console.log(`Updating ${storiesBatch.length} stories`) 
    db.Story.bulkWrite(storiesBatch)
}

console.log(`Finished updating stories`)