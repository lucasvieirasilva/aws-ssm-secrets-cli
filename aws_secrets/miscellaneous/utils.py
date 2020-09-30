def parse_tags(resource):
    tags = []
    if 'tags' in resource:
        for key in resource['tags'].keys():
            tags.append({
                'Key': key,
                'Value': resource['tags'][key]
            })
    return tags


def repeat_to_length(string_to_expand, length):
    return (string_to_expand * (int(length/len(string_to_expand))+1))[:length]
