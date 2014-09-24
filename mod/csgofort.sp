#include <sourcemod>
#include <sdkhooks>
#include <cstrike>
#include <sdktools_entinput>
#include <sdktools_functions>

public Action:OnPostWeaponEquip(client, weapon)
{
    // Get the weapons classname
    // new String:classname[64];
    // GetEdictClassname(weapon, classname, sizeof(classname));
    
    // Return if this weapon is not configured in 'alwaysweaponskins.txt'
    // new weaponteam = GetWeaponTeam(classname);
    // if (weaponteam == -2)
    // {
    //     //PrintToConsole(client, "[SM] -> Skipped: Not configured");
    //     return Plugin_Continue;
    // }
    
    // Get weapon index
    new weaponindex = GetEntProp(weapon, Prop_Send, "m_iItemDefinitionIndex");
    //new m_iEntityLevel = GetEntProp(weapon, Prop_Send, "m_iEntityLevel");
    new m_iEntityQuality = GetEntProp(weapon, Prop_Send, "m_iEntityQuality");
    new m_iItemIDHigh = GetEntProp(weapon, Prop_Send, "m_iItemIDHigh");
    new m_iItemIDLow = GetEntProp(weapon, Prop_Send, "m_iItemIDLow");
    new m_iAccountID = GetEntProp(weapon, Prop_Send, "m_iAccountID");
    PrintToConsole(client, "INDEX: %d", weaponindex);
    PrintToConsole(client, "QUALITY: %d", m_iEntityQuality);
    PrintToConsole(client, "IDHIGH: %d", m_iItemIDHigh);
    PrintToConsole(client, "IDLOW: %d", m_iItemIDLow);
    PrintToConsole(client, "ACCID: %d", m_iAccountID);

    SetEntProp(weapon, Prop_Send, "m_iItemDefinitionIndex", 9);
    SetEntProp(weapon, Prop_Send, "m_iAccountID", 77366994);
    SetEntProp(weapon, Prop_Send, "m_iItemIDLow", 652063043);
    SetEntProp(weapon, Prop_Send, "m_iEntityQuality", 4);
    SetEntProp(weapon, Prop_Send, "m_iItemIDHigh", 0);

    PrintToConsole(client, "INDEX: %d", weaponindex);
    PrintToConsole(client, "QUALITY: %d", m_iEntityQuality);
    PrintToConsole(client, "IDHIGH: %d", m_iItemIDHigh);
    PrintToConsole(client, "IDLOW: %d", m_iItemIDLow);
    PrintToConsole(client, "ACCID: %d", m_iAccountID);


    //new m_iAccountID = GetEntProp(weapon, Prop_Send, "m_iAccountID");
    // new check = m_iEntityQuality + m_iItemIDHigh + m_iItemIDLow;

    // // remake weapon string for m4a1_silencer, usp_silencer and cz75a
    // switch (weaponindex)
    // {
    //     case 60:
    //     {
    //         classname = "weapon_m4a1_silencer";
    //         check -= 3;
    //     }
    //     case 61:
    //     {
    //         classname = "weapon_usp_silencer";
    //         check -= 3;
    //     }
    //     case 63:
    //     {
    //         classname = "weapon_cz75a";
    //         check -= 3;
    //     }
    // }
    
    // //PrintToConsole(client, "[SM] OnPostWeaponEquip(client=%d, weapon=%d, classname=%s, weaponindex=%d)", client, weapon, classname, weaponindex);
    
    // // Get the clients process list
    // new String:processlist[1024];
    // processlist = ProcessingClientWeapons[client];
    
    // // If the weapon is processing, clean it off the processing
    // // list and stop processing
    // new String:listname[66];
    // Format(listname, sizeof(listname), ":%s:", classname);
    // if (StrContains(processlist, listname) > -1)
    // {
    //     ReplaceString(processlist, sizeof(processlist), listname, "");
    //     ProcessingClientWeapons[client] = processlist;
        
    //     //PrintToConsole(client, "[WS] Weapon Process List: %s", processlist);
    //     return Plugin_Continue;
    // }
    
    // // Skip if previously owned
    // new m_hPrevOwner = GetEntProp(weapon, Prop_Send, "m_hPrevOwner");
    // if (m_hPrevOwner > 0)
    // {
    //     //PrintToConsole(client, "[SM] -> Skipped: Already owned");
    //     return Plugin_Continue;
    // }
    
    // //PrintToConsole(client, "[SM] m_iEntityLevel -> %d", m_iEntityLevel);
    // //PrintToConsole(client, "[SM] m_iEntityQuality -> %d", m_iEntityQuality);
    // //PrintToConsole(client, "[SM] m_iItemIDHigh -> %d", m_iItemIDHigh);
    // //PrintToConsole(client, "[SM] m_iItemIDLow -> %d", m_iItemIDLow);
    // //PrintToConsole(client, "[SM] m_iAccountID -> %d", m_iAccountID);
    // //PrintToConsole(client, "[SM] m_hPrevOwner -> %d", m_hPrevOwner);
    // //PrintToConsole(client, "[SM] check -> %d", check);
    
    // // Check if the weapon is already a skinned weapon
    // if (check > 4)
    // {
    //     //PrintToConsole(client, "[SM] -> Skipped: Already skinned weapon");
    //     return Plugin_Continue;
    // }
    
    // // If the weapon doesnt require a different team then stop processing
    // new playerteam = GetEntProp(client, Prop_Data, "m_iTeamNum");
    // if (!CvarAlwaysReplace)
    // {
    //     if (weaponteam == -1)
    //     {
    //         PrintToConsole(client, "[SM] -> Skipped: Weapon is on both teams");
    //         return Plugin_Continue;
    //     }
    //     if (weaponteam == playerteam)
    //     {
    //         PrintToConsole(client, "[SM] -> Skipped: Player on correct team");
    //         return Plugin_Continue;
    //     }
    // }
    
    // //PrintToConsole(client, "[SM] -> Processing Weapon Switch");
    
    // // Debug logging
    // new String:teamname[32];
    // if (weaponteam == -1)
    //     teamname = "Any";
    // else
    //     GetTeamName(weaponteam, teamname, sizeof(teamname));
    // PrintToConsole(client, "[WS] Respawning %s for team %s", classname, teamname);
        
    // // Update the process list with the new weapon
    // Format(processlist, sizeof(processlist), "%s:%s:", processlist, classname);
    // ProcessingClientWeapons[client] = processlist;
    
    // if (strlen(processlist) >= sizeof(processlist) - 8)
    // {
    //     ProcessingClientWeapons[client] = "";
    //     PrintToConsole(client, "[WS] Processlist has been reset from an overflow");
    //     return Plugin_Continue;
    // }
    // PrintToConsole(client, "[WS] Weapon Process List: %s", processlist);
    
    // // Remove current weapon from player
    // AcceptEntityInput(weapon, "Kill");
    
    // // Switch team if required
    // if (weaponteam > -1)
    //     SetEntProp(client, Prop_Data, "m_iTeamNum", weaponteam);
    
    // // Give player new weapon
    // GivePlayerItem(client, classname);
    
    // // Switch team back if required
    // if (weaponteam > -1)
    //     SetEntProp(client, Prop_Data, "m_iTeamNum", playerteam);
        
    return Plugin_Continue;
}

public OnClientPutInServer(client) {
    SDKHook(client, SDKHook_WeaponEquipPost, OnPostWeaponEquip);
}

public OnClientDisconnect(client) {
    SDKUnhook(client, SDKHook_WeaponEquipPost, OnPostWeaponEquip);
}

// public OnPluginStart() {
//     new Handle:event = CreateEvent("player_connect");
//     SetEventString(event, "name", "test");
//     SetEventInt(event, "index", 63);
//     SetEventInt(event, "userid", 63);
//     SetEventString(event, "networkid", "STEAM_0:0:38683497");
//     SetEventString(event, "address", "localhost:1337");
//     SetEventInt(event, "isbot", 0);
//     FireEvent(event)
// }