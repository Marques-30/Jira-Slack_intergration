from jira import JIRA
from errbot import BotPlugin, botcmd
import os, sys, re, time

jira = jira = JIRA(auth=('username', 'jira_password'), options={'server': "Jira Url"})

class jiraChannel(BotPlugin):

    @botcmd
    def jira_open(self, msg, args):
      """Use this command to create Jira Request Tickets: `!jira open 'Project Key'; 'Summary'; 'Description'`"""
      user = str(msg.frm).split("/")[0]
      user_identifier = self.build_identifier(f"{user}")
      Spacer = str(msg).split("open")[1]
      Topic = Spacer.split(";")[1]
      Detail = str(msg).split(";")[2]
      name = str(user_identifier).split("@")[1]
      username = name
      proj = Spacer.split(";")[0]
      if proj.upper() == " ASKSEC":
         new_issue = jira.create_issue(project ="10205", summary = Topic,
                                       description = Detail, issuetype={'name': 'Service Request'})
      elif proj.upper() == " JR":
         new_issue = jira.create_issue(project ="10316", summary = Topic,
                                       description = Detail, issuetype={'name': 'Task'})
      elif proj.upper() == " CORPSRE":
         new_issue = jira.create_issue(project ="11400", summary = Topic,
                                       description = Detail, issuetype={'name': 'Story'})
      else:
         print()
      for issue in jira.search_issues("reporter = 'username' order by created DESC", maxResults =1):
         """Say a card in the chatroom."""
         self.send_card(title=f"Thank you, {user_identifier}",
                         body='A' + proj + ' ticket has been made with the Jira Team and someone will be reaching out to you shortly about this.',
                         thumbnail='https://raw.githubusercontent.com/errbotio/errbot/master/docs/_static/errbot.png',
                         link='Jira Instance URL' + issue.key,
                         fields=(('Summary', issue.fields.summary), ('Description', issue.fields.description)),
                         color='blue',
                         in_reply_to=msg)
      time.sleep(30)
      issue.update(reporter={'name': username})

    @botcmd
    def jira_close(self, msg, args):
      """Use this command to close out Jira Tickets: `!jira close 'ticket number'`"""
      spacer = str(msg).split("close ")[1]
      Key = spacer.split(";")[0]
      user = str(msg.frm).split("/")[0]
      user_identifier = self.build_identifier(f"{user}")
      name = str(user_identifier).split("@")[1]
      username = name
      issue = jira.issue(Key)
      proj = Key.split("-")[0]
      end = 'This ticket had been closed by ' + name
      if proj == "ASKSEC":
         jira.transition_issue(issue, transition='12')
         comment = jira.add_comment(Key, end)
      elif proj == "JR":
         jira.transition_issue(issue, transition='91')
         comment = jira.add_comment(Key, end)
      elif proj == "CORPSRE":
         jira.transition_issue(issue, transition='3')
         comment = jira.add_comment(Key, end)
      else:
         print("Project needs to be added to close out list in errbot")
      self.send_card(title=f"Hello {user_identifier},",
                      body='The following ticket has been closed ' + name,
                      thumbnail='https://raw.githubusercontent.com/errbotio/errbot/master/docs/_static/errbot.png',
                      link='Jira Instance URL' + Key,
                      fields=(('Project Key', issue.key), ('comment', end)),
                      color='blue',
                      in_reply_to=msg)


    @botcmd
    def jira_comment(self, msg, args):
      """Use this command to comment on Jira Tickets: `!jira comment 'Ticket number'; 'comment'`"""
      spacer = str(msg).split("comment ")[1]
      Key = spacer.split(";")[0]
      user = str(msg.frm).split("/")[0]
      user_identifier = self.build_identifier(f"{user}")
      comments = spacer.split(";")[1]
      comment = jira.add_comment(Key, comments)
      """Say a card in the chatroom."""
      self.send_card(title=f"Hello {user_identifier},",
                      body='The following comment has been added to the ticket',
                      link='Jira Instance' + Key,
                      thumbnail='https://raw.githubusercontent.com/errbotio/errbot/master/docs/_static/errbot.png',
                      fields=(('Issue', Key), ('Comment', comments)),
                      color='blue',
                      in_reply_to=msg)

    @botcmd
    def jira_list(self, msg, args):
      """List of all jira user is currently assigned: `!jira list`"""
      #self.log.info(str(msg))
      #self.log.info(str(msg.identifier))
      user = str(msg.frm).split("/")[0]
      user_identifier = self.build_identifier(f"{user}")
      name = str(user_identifier).split("@")[1]
      username = name
      for issue in jira.search_issues("assignee = '" + username + "' AND status not in (Done, Cancelled, Resolved, Closed) order by created DESC", maxResults=15):
         hyperlink = "<Jira URL" + issue.key + "|" + issue.key + ">"
         self.send_card(
             color='blue',
             summary=hyperlink,
             link = hyperlink,
             body=issue.fields.summary,
             thumbnail=issue.fields.status.iconUrl,
             image=issue.fields.status.iconUrl,
             #fields=(("Status", issue.fields.status.name), ("Reporter", issue.fields.reporter.displayName), ("Priority", issue.fields.priority.name)),
             fields=(("Status", issue.fields.status.name), ("Priority", issue.fields.priority.name)),
             in_reply_to=msg)

    @botcmd
    def jira_attach(self, msg, args):
      """Use this command to add attachments to Jira tickets: `!jira attach 'Ticket number'; 'file path of attachment'`"""
      spacer = str(msg).split("attach ")[1]
      Key = spacer.split(";")[0]
      attach = spacer.split(";")[1]
      user = str(msg.frm).split("/")[0]
      user_identifier = self.build_identifier(f"{user}")
      comments = spacer.split(";")[1]
      jira.add_attachment(issue= Key, attachment= attach)
      """Say a card in the chatroom."""
      self.send_card(title=f"Hello {user_identifier},",
                      body='The attachment has been successfully uploaded to the Jira Ticket: ' + Key,
                      thumbnail='https://raw.githubusercontent.com/errbotio/errbot/master/docs/_static/errbot.png',
                      color='blue',
                      in_reply_to=msg)

    @botcmd
    def jira_report(self, msg, args):
      """List of all jira tickets that you are the reporter for: `!jira report`"""
      user = str(msg.frm).split("/")[0]
      user_identifier = self.build_identifier(f"{user}")
      name = str(user_identifier).split("@")[1]
      username = name
      for issue in jira.search_issues("assignee is not EMPTY AND reporter = '" + username + "' AND status not in (Done, Cancelled, Resolved, Closed) order by created DESC", maxResults=15):
         hyperlink = "Jira Instance URL" + issue.key + "|" + issue.key + ">"
         try:
            assign = issue.fields.assignee.displayName
         except NameError:
            assign = "Unassigned"
         self.send_card(
             color='blue',
             summary=hyperlink,
             link = hyperlink,
             body=issue.fields.summary,
             thumbnail=issue.fields.status.iconUrl,
             image=issue.fields.status.iconUrl,
             fields=(("Assignee", assign), ("Status", issue.fields.status.name)),
             in_reply_to=msg)
