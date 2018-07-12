# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class IntelligentGameApi(models.Model):
    _inherit = "og.igame"

    @api.model
    @api.returns('self')
    def create_bridge_game(self,name,org_type=None, score_uom=None):
        vals = {'name':name, 'game_type':'bridge', 'match_type':'team'}
        if org_type: vals['org_type'] = org_type
        if score_uom: vals['score_uom'] = score_uom
        gid = self.create(vals)
        return gid

    @api.model
    @api.returns('self')
    def create_child(self,name,parent_id,org_type=None,sequence=None):
        vals = {'name':name, 'parent_id': parent_id}
        parent = self.env['og.igame'].browse(parent_id)
        vals['game_type'] = parent.game_type
        vals['match_type'] = parent.match_type
        if org_type: vals['org_type'] = org_type
        if sequence: vals['sequence'] = sequence
        vals['score_uom'] = parent.score_uom
        return self.create(vals)

    @api.model
    @api.returns('self')
    def search_bridge_game(self,domain):
        self = self.sudo()
        dm = [('parent_id','=',None),('game_type','=','bridge'),
              ('match_type','=','team')  ] + domain
        gms = self.env['og.igame'].search(dm)
        return gms

    @api.model
    def search2(self,domain):
        gms = self.search_bridge_game(domain=domain)
        return [{'name': gm.name, 'id': gm.id,'datetime':gm.date_game,'type':gm.match_type
                 ,'referee':gm.referee,'arbitrator':gm.arbitrator,'host_unit':gm.host_unit
                 ,'sponsor':gm.sponsor} for gm in gms]


    @api.model
    def search_user(self,user_id):
        us = self.env['res.users'].search([('id','=',user_id)])
        pa = self.env['res.partner'].search([('id','=',us.partner_id.id)])
        team = self.env['og.igame.team'].search([('partner_id', '=', pa.parent_id.id)])
        games = self.env['og.igame'].search([('id', '=', team.igame_id.id)])
        return games

    @api.model
    def search_user_match(self, user_id):
        games = self.search_user(user_id)
        return [{'name': game.name, 'id': game.id,'datetime':game.date_game,'type':game.match_type
                 ,'state':game.state,'referee':game.referee,'arbitrator':game.arbitrator,'host_unit':game.host_unit
                 ,'sponsor':game.sponsor}for game in games]

    @api.model
    # @api.returns('self')
    def search_own_match(self,user_id):

        us = self.env['res.users'].search([('id','=',user_id)])
        pa = self.env['res.partner'].search([('id','=',us.partner_id.id)])
        if pa.parent_id is not None:
            team = self.env['og.igame.team'].search([('partner_id', '=', pa.parent_id.id)])
            games = self.env['og.igame'].search([])

            arr = []

            for g in games:
                if team.igame_id.id == g.id:
                    arr.append([{'name': g.name, 'id': g.id,'datetime':g.date_game,'type':g.match_type
                     ,'state':g.state,'referee':g.referee,'arbitrator':g.arbitrator,'host_unit':g.host_unit
                     ,'sponsor':g.sponsor,'tt':True}])

                else:
                    arr.append([{'name': g.name, 'id': g.id,'datetime':g.date_game,'type':g.match_type
                 ,'state':g.state,'referee':g.referee,'arbitrator':g.arbitrator,'host_unit':g.host_unit
                 ,'sponsor':g.sponsor,'tt':False}])
            return arr
        else:
            # team = self.env['og.igame.team'].search([('partner_id', '=', pa.parent_id.id)])
            games = self.env['og.igame'].search([])
            arr = []
            for g in games:
                arr.append([{'name': g.name, 'id': g.id,'datetime':g.date_game,'type':g.match_type
                     ,'state':g.state,'referee':g.referee,'arbitrator':g.arbitrator,'host_unit':g.host_unit
                     ,'sponsor':g.sponsor,'tt':False}])
            return arr


    @api.multi
    def search_rounds_details(self):
        rs = self.env['og.igame.round'].search([('igame_id','=',self.id)  ] )
        # r.team_line_ids = rd
        return [{'id':r.id,'number':r.number,'name':r.name}for r in rs]

    @api.model
    def search_round_details(self,round_id):
        r = self.env['og.igame.team.line'].search([('round_id','=',round_id)])

        ms = self.env['og.match'].search([('id','=',r.match_id.id)])

        return ms

    @api.model
    def search_round_details(self,round_id):
        ms = self.search_round_details(round_id)
        return [{}]

    @api.multi
    def set_group(self, group_name, number):
        gid = self.id
        # gs = self.group_ids.filtered(lambda g: g.name == group_name)

        gs = self.env['og.igame.group'].search(
              [('name','=',group_name),('igame_id','=',gid)  ] )

        g = gs and gs[0] or None
        if not g:
            vals = {'igame_id':gid,'name':group_name}
            g = self.env['og.igame.group'].create(vals)

        return True

    @api.model
    def get_users(self):
        dm=[]
        a=[]
        users=self.env['res.users'].search(dm)
        for rec in users:
            if not rec.partner_id.name == 'Administrator':
                a.append({'id':rec.partner_id.id,'name':rec.partner_id.name})
        return a

    @api.model
    # @api.returns('self')
    def register_game(self,game_id,team_id,kwargs):
        self=self.sudo()
        iteam=self.env['og.igame.team'].search([('partner_id','=',team_id),('igame_id','=',None)])
        vals={'igame_id':game_id,'partner_id':iteam.partner_id.id}
        new_team=self.env['og.igame.team'].create(vals)
        for rec in kwargs:
            player_id=rec['id']
            role=rec['role']
            vals={'partner_id':player_id,'role':role,'team_id':new_team.id}
            self.env['og.igame.team.player'].create(vals)
        return True


class IntelligentGameTeam(models.Model):
    _inherit = "og.igame.team"

    # $$$$$
    # create a team,where team info are added into 'res.partner' and 'og.igame team'
    # the parent_id field of a team in 'res.partner' points to user that creates the team
    # and the og.igame.team's partner_id points to the id of a team in 'res.partner'
    # and no game_id is added to the og.igame.team in this function which indicates that the team created here
    # only represents a team,where you can add players
    #
    @api.model
    # @api.returns('self')
    # def create_team(self,team_name,kwargs):
    def create_team(self, team_name, kwargs):
        user_id = self.env.user.id
        user = self.env['res.users'].search([('id', '=', user_id)])
        partner = user.partner_id
        # user's partner info
        self = self.sudo()
        team_id = self.env['res.partner'].search([('name', '=', team_name)])
        if team_id: return False
        vals = {'name': team_name}
        t = self.env['res.partner'].create(vals)
        # create team in res.parner
        # team=self.env['res.partner'].search([('name','=',team_name)])
        info = {'parent_id': partner.id, 'partner_id': t.id}
        tid = self.create(info)
        # s=tid.id
        # link a team in res.partner to og.igame.team which means a team you can add players
        for player in kwargs:
            vals = {'partner_id': player, 'team_id': tid.id}
            self.env['og.igame.team.player'].create(vals)
        # add player to the team
        # default role : "player"
        return t.id

    # $$$$$
    # get players that belong to a team
    # trigger the team and returns a list of players
    @api.model
    def get_teamplayer(self, team_id):
        self = self.sudo()
        team = self.browse(team_id)
        players = team.player_ids
        player = [{'id': rec.partner_id.id, 'name': rec.partner_id.name} for rec in players]
        return player

    # get all the teams of a user,returns team.id and team name and player's name !!!!!!!!
    @api.model
    # @api.returns('self')
    def get_teams(self):
        res = []

        user = self.env.user.partner_id  # get user'partner
        self = self.sudo()
        player = self.env['og.igame.team.player'].search(
            [('partner_id', '=', user.id), ('role', '=', None)])  # get teams of a player
        # team=self.env['res.partner'].search([('parent_id','=',user.id)])
        # t=player[0].team_id.player_ids
        for rec in player:
            players = rec.team_id.player_ids
            team = rec.team_id.partner_id
            #   players=team.player_ids # find players of a team in og.igame.team.players
            cache = []
            for attendee in players:
                player_id = attendee.partner_id.id
                player_name = attendee.partner_id.name
                player_info = {'id': player_id, 'playername': player_name}
                cache.append(player_info)
            info = {'id': team.id, 'teamname': team.name, 'players': cache}
            res.append(info)
        return res

    # get all the teams where I am the creator
    @api.model
    def get_own_teams(self):
        res = []
        user = self.env.user.partner_id  # get user'partner
        self = self.sudo()
        own_team = self.env['res.partner'].search([('parent_id', '=', user.id)])

        for rec in own_team:
            team_id = rec.id
            iteam = self.env['og.igame.team'].search([('partner_id', '=', team_id), ('igame_id', '=', None)])
            iplayers = iteam.player_ids
            cache = []
            for attendee in iplayers:
                player_id = attendee.partner_id.id
                player_name = attendee.partner_id.name
                player_info = {'id': player_id, 'playername': player_name}
                cache.append(player_info)
            info = {'id': team_id, 'teamname': rec.name, 'players': cache}
            res.append(info)
        return res


class IntelligentTeamPlayer(models.Model):
    _inherit = 'og.igame.team.player'

    @api.model
    @api.returns('self')
    def create_player(self, player_name, team_name, game_name, role='player'):
        self = self.sudo()
        player_id = self.env['res.partner'].search([('name', '=', player_name)])
        game_id = self.env['og.igame'].search([('name', '=', game_name)])
        team_id = self.env['res.partner'].search([('name', '=', team_name)])
        iteam_id = self.env['og.igame.team'].search([('igame_id', '=', game_id.id),
                                                     ('partner_id', '=', team_id.id)])
        info = {'team_id': iteam_id.id, 'partner_id': player_id.id, 'role': role}
        pid = self.create(info)
        return pid


class IntelligentGameGroup(models.Model):
    _inherit = "og.igame.group"

    @api.model
    @api.returns('self')
    def search_bridge_group(self,domain):

        dm = domain

        groups = self.env['og.igame.group'].search(dm)
        return groups  #self.env['og.igame'].browse(gid)
        #return [{'name':gm.name, 'id':gm.id}  for gm in gms ]

    @api.model
    def search_group(self,domain):
        groups = self.search_bridge_group(domain=domain)
        return [{'name': group.name, 'id': group.id} for group in groups]
        # return [{'name': gm.name, 'id': gm.id} for gm in gms]

    # @api.model
    # def del_group(self,group_id):
    #     sc = self.search(group_id)
    #     if sc:
    #         sc.unlink()

    @api.multi
    # @api.returns('self')
    def add_team(self,team_id,number):

        team = self.env['og.igame.team'].browse(team_id)
        team.group_id = self.id
        team.number = number

        return True

    @api.multi
    def del_team(self, team_id):

        sc = self.env['og.igame.team'].browse(team_id)
        sc.group_id = None


class IntelligentGameRound(models.Model):
    _inherit = "og.igame.round"

    @api.model
    @api.returns('self')
    def create_bridge_round(self, igame_id, number):
        #gs = self.group_ids.filtered(lambda g: g.name == group_name)

        gs = self.env['og.igame.round'].search(
              [('igame_id','=',igame_id)  ] )

        vals = {'igame_id':igame_id,'round':number}
        g = self.env['og.igame.round'].create(vals)

        return g

    @api.model
    @api.returns('self')
    def search_bridge_round(self,igame_id):
        gs = self.env['og.igame.round'].search(
              [('igame_id','=',igame_id)  ] )

        return gs


    @api.multi
    # @api.returns('self')
    def add_bridge_deals(self,deal_id):

        gs = self.search( [('id', '=', self.id)])
        gd = self.env['og.deal'].search([('id', '=', deal_id)])
        gs.deal_ids = gd

        return True

    @api.multi
    # @api.returns('self')
    def del_bridge_deals(self,deal_id):
        gs = self.search([('id', '=', self.id)])
        gd = self.env['og.deal'].search([('id', '=', deal_id)])
        # gd.unlink()
        # c = [g.id for g in gs.deal_ids]
        #
        # c.remove(gd.id)
        c = self.deal_ids - gd
        self.deal_ids = c

        return self.deal_ids

    @api.model
    def round_match(self):
        tm = self.env['og.igame.group'].search([])



        return tm

    @api.multi
    def create_table(self,table_id):
        tt = self.search([('id','=',self.id)])
        tb = self.env['og.table'].search([('id', '=', table_id)])
        tt.table_ids = tb


        return tt

# class IntelligentGameTeamLine(models.Model):
#     _inherit = "og.igame.team.line"
#
#     @api.model
#     def create_team_line(self,team_id):
#



