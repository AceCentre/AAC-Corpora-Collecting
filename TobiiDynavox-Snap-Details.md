Exports are .sps files. these are sqlite files. no encryption. 


here is the sttructre


```sql

BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS "CommandSequence" (
	"Id"	integer NOT NULL,
	"SerializedCommands"	varchar,
	"ButtonId"	integer,
	PRIMARY KEY("Id" AUTOINCREMENT)
);
CREATE TABLE IF NOT EXISTS "ButtonPlacement" (
	"Id"	integer NOT NULL,
	"GridPosition"	varchar,
	"Visible"	integer,
	"ButtonId"	integer,
	"PageLayoutId"	integer,
	PRIMARY KEY("Id" AUTOINCREMENT)
);
CREATE TABLE IF NOT EXISTS "PageLayout" (
	"Id"	integer NOT NULL,
	"PageLayoutSetting"	varchar,
	"PageId"	integer,
	PRIMARY KEY("Id" AUTOINCREMENT)
);
CREATE TABLE IF NOT EXISTS "PageExtra" (
	"Id"	integer,
	"AccessedAt"	bigint,
	PRIMARY KEY("Id"),
	FOREIGN KEY("Id") REFERENCES "Page"("Id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "PageSetData" (
	"Id"	integer NOT NULL,
	"Identifier"	varchar,
	"Data"	blob,
	"RefCount"	integer DEFAULT 0,
	PRIMARY KEY("Id" AUTOINCREMENT)
);
CREATE TABLE IF NOT EXISTS "SyncData" (
	"UniqueId"	varchar(36) NOT NULL,
	"Type"	integer,
	"Timestamp"	bigint,
	"SyncHash"	integer,
	"Deleted"	integer,
	"Description"	VARCHAR,
	PRIMARY KEY("UniqueId")
);
CREATE TABLE IF NOT EXISTS "Synchronization" (
	"Id"	integer NOT NULL,
	"SyncServerIdentifier"	varchar,
	"PageSetTimestamp"	bigint,
	"PageSetSyncHash"	integer,
	PRIMARY KEY("Id" AUTOINCREMENT)
);
CREATE TABLE IF NOT EXISTS "Page" (
	"Id"	integer NOT NULL,
	"UniqueId"	varchar(36),
	"Title"	varchar,
	"PageType"	integer,
	"Language"	varchar,
	"BackgroundColor"	integer,
	"ContentTag"	varchar,
	"Timestamp"	bigint,
	"SyncHash"	integer,
	"LibrarySymbolId"	integer,
	"PageSetImageId"	integer,
	"GridDimension"	varchar,
	"MessageBarVisible"	integer,
	PRIMARY KEY("Id" AUTOINCREMENT)
);
CREATE TABLE IF NOT EXISTS "PageSetProperties" (
	"Id"	integer,
	"ContentIdentifier"	VARCHAR,
	"ContentVersion"	VARCHAR,
	"SchemaVersion"	VARCHAR,
	"UniqueId"	VARCHAR(36),
	"Language"	VARCHAR,
	"Timestamp"	BIGINT,
	"SyncHash"	integer,
	"DefaultHomePageUniqueId"	VARCHAR(36),
	"SerializedHomePageUniqueIdOverrides"	BLOB,
	"DefaultKeyboardPageUniqueId"	VARCHAR(36),
	"SerializedKeyboardPageUniqueIdOverrides"	BLOB,
	"ToolBarUniqueId"	VARCHAR(36),
	"DashboardUniqueId"	VARCHAR(36),
	"MessageBarUniqueId"	VARCHAR(36),
	"MessageBarVisible"	integer,
	"ToolBarVisible"	integer,
	"FriendlyName"	VARCHAR,
	"Description"	VARCHAR,
	"IconImageId"	integer,
	"SerializedPreferredGridDimensions"	VARCHAR,
	"GridDimension"	VARCHAR,
	"SmartSymLayout"	integer,
	"FontFamily"	VARCHAR,
	"FontSize"	float,
	"FontStyle"	int,
	"PageBackgroundColor"	integer,
	"MessageBarBackgroundColor"	integer,
	"ToolBarBackgroundColor"	integer,
	"MessageWindowTextColor"	integer,
	"MessageWindowFontSize"	float,
	PRIMARY KEY("Id")
);
CREATE TABLE IF NOT EXISTS "ButtonPageLink" (
	"Id"	INTEGER NOT NULL,
	"ButtonId"	INTEGER NOT NULL,
	"PageUniqueId"	varchar(36) NOT NULL,
	PRIMARY KEY("Id" AUTOINCREMENT),
	FOREIGN KEY("ButtonId") REFERENCES "Button"("Id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "Button" (
	"Id"	INTEGER NOT NULL,
	"Language"	varchar,
	"Label"	varchar,
	"LabelOwnership"	integer,
	"Message"	varchar,
	"AudioCue"	varchar,
	"ImageOwnership"	integer,
	"LabelColor"	integer,
	"BackgroundColor"	integer,
	"BorderColor"	integer,
	"BorderThickness"	float,
	"FontSize"	float,
	"FontFamily"	varchar,
	"FontStyle"	integer,
	"SmartSymLayout"	integer,
	"CommandFlags"	integer,
	"ContentType"	integer,
	"ContentTag"	varchar,
	"LibrarySymbolId"	integer,
	"PageSetImageId"	integer,
	"SerializedContentTypeHandler"	varchar,
	"MessageRecordingId"	integer,
	"AudioCueRecordingId"	integer,
	"PageId"	integer,
	"UseMessageRecording"	integer,
	"UseAudioCueRecording"	integer,
	"UniqueId"	varchar(36),
	PRIMARY KEY("Id" AUTOINCREMENT)
);
CREATE INDEX IF NOT EXISTS "CommandSequence_ButtonId" ON "CommandSequence" (
	"ButtonId"
);
CREATE INDEX IF NOT EXISTS "ButtonPlacement_PageLayoutId" ON "ButtonPlacement" (
	"PageLayoutId"
);
CREATE INDEX IF NOT EXISTS "PageLayout_PageId" ON "PageLayout" (
	"PageId"
);
CREATE INDEX IF NOT EXISTS "Button_AudioCueRecordingId" ON "Button" (
	"AudioCueRecordingId"
);
CREATE INDEX IF NOT EXISTS "Button_MessageRecordingId" ON "Button" (
	"MessageRecordingId"
);
CREATE INDEX IF NOT EXISTS "Button_PageId" ON "Button" (
	"PageId"
);
CREATE INDEX IF NOT EXISTS "Button_PageSetImageId" ON "Button" (
	"PageSetImageId"
);
CREATE UNIQUE INDEX IF NOT EXISTS "PageSetData_Identifier" ON "PageSetData" (
	"Identifier"
);
CREATE UNIQUE INDEX IF NOT EXISTS "Page_UniqueId" ON "Page" (
	"UniqueId"
);
CREATE INDEX IF NOT EXISTS "Page_PageSetImageId" ON "Page" (
	"PageSetImageId"
);
COMMIT;

```
