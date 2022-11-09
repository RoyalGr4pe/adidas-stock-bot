def get_members(client):
    member_names = []
    for guild in client.guilds:
        for member in guild.members:
            if member.bot != True:
                member_names.append(member.name)
    return member_names