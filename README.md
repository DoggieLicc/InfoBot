Invite this bot: https://discord.com/oauth2/authorize?client_id=818281562042138635&permissions=2048&scope=bot
# InfoBot
This bot gets information about certain discord objects, such as users, channels, roles, the server, emotes, and invite links
## Commands:
**prefix:** *info$*
### help [command]
Returns information about the specified command, if there is no command specified, it will list the commands
### channel <channel>
Returns information about the specified channel, It returns: *Slowmode status, Channel type, Category, Channel ID, and the creation date.*
### emote <emote>
Returns information about the specified emote, it returns: *Emote name, emote ID, and creation date*
### invite <invite>
Returns information about the specified emote, it returns: *The invite channel and ID,  Server name and icon and amount of members, and the creation date of the server*
### role <role>
Returns information about the specified role, it returns: *Amount of members with role, role name, position, ID, role hex color, important permissions, and the creation date.*
### user [user]
Returns information about the specified user, it returns: *Bot status, ID, avatar, and creation date of user*
If the user is in the current server, it returns more info: *Date the member joined the server, the highest role, list of the roles the member has, and the list of important permissions the member has.*
If there is no user specified, it returns information for the user using the command
### server [subcommand]
Without subcommand: Returns information about the current server, it returns: *Special features of the server, boost level, the owner, region, amount of members, amount of roles, amount of boosters, amount of channels, ID, and the creation date of the server*
#### server subcommands
##### server list_roles
Lists all of the roles in the server, along with info for each role. To stop spam, roles are sent to the user's DMs
##### server list_channels
Lists all of the channels in the server, along with info for each role. To stop spam, channels will be sent to the user's DMs
##### server list_emotes
Lists all of the emotes in the server
