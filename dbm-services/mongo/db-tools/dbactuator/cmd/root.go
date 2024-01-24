// Package cmd 根目录
/*
Copyright © 2022 NAME HERE <EMAIL ADDRESS>

*/
package cmd

import (
	"encoding/base64"
	"fmt"
	"log"
	"os"

	"dbm-services/mongo/db-tools/dbactuator/pkg/consts"
	"dbm-services/mongo/db-tools/dbactuator/pkg/jobmanager"
	"dbm-services/mongo/db-tools/dbactuator/pkg/util"

	"github.com/spf13/cobra"
)

var uid string
var rootID string
var nodeID string
var versionID string
var dataDir string
var backupDir string
var payLoad string
var payLoadFormat string
var payLoadFile string
var atomJobList string
var user string
var group string
var printParamJson string
var listJob bool

// RootCmd represents the base command when called without any subcommands
var RootCmd = &cobra.Command{
	Use:   "mongo-dbactuator",
	Short: "mongo原子任务合集",
	Long:  `mongo原子任务合集,包含mongo复制集、cluster的创建，备份，回档等等原子任务。`,
	// Uncomment the following line if your bare application
	// has an action associated with it:
	Run: func(cmd *cobra.Command, args []string) {
		var err error
		dir, _ := util.GetCurrentDirectory()

		// 优先使用payLoad。 payLoadFile 个人测试的时候使用的.
		if payLoad == "" && payLoadFile != "" {
			if o, err := os.ReadFile(payLoadFile); err == nil {
				payLoad = base64.StdEncoding.EncodeToString(o)
				log.Printf("using payload file %s", payLoadFile)
			} else {
				log.Printf("using payload file %s err %v", payLoadFile, err)
			}
		}

		// 设置mongo环境变量
		err = consts.SetMongoDataDir(dataDir)
		if err != nil {
			log.Println(err.Error())
			os.Exit(-1)
		}
		err = consts.SetMongoBackupDir(backupDir)
		if err != nil {
			log.Println(err.Error())
			os.Exit(-1)
		}

		err = consts.SetProcessUser(user)
		if err != nil {
			log.Println(err.Error())
			os.Exit(-1)
		}
		err = consts.SetProcessUserGroup(group)
		if err != nil {
			log.Println(err.Error())
			os.Exit(-1)
		}

		manager, err := jobmanager.NewJobGenericManager(uid, rootID, nodeID, versionID,
			payLoad, payLoadFormat, atomJobList, dir)
		if err != nil {
			return
		}
		err = manager.LoadAtomJobs()
		if err != nil {
			os.Exit(-1)
		}
		err = manager.RunAtomJobs()
		if err != nil {
			os.Exit(-1)
		}
	},
}

var debugCmd = &cobra.Command{
	Use:   "debug",
	Short: "debug",
	Long:  `debug`,
	Run: func(cmd *cobra.Command, args []string) {
		if listJob {
			dir, _ := util.GetCurrentDirectory()
			if manager, err := jobmanager.NewJobGenericManager(uid, rootID, nodeID, versionID,
				payLoad, payLoadFormat, atomJobList, dir); err != nil {
				panic(err)
			} else {
				manager.RegisterAtomJob()
				for _, r := range manager.GetJobNameList() {
					fmt.Printf("%s\n", r)
				}
			}
			os.Exit(0)
		} else if printParamJson != "" {
			doPrintParamJson()
		} else {
			cmd.Help()
		}
	},
}

func init() {
	// Here you will define your flags and configuration settings.
	// Cobra supports persistent flags, which, if defined here,
	// will be global for your application.

	// Cobra also supports local flags, which will only run
	// when this action is called directly.
	RootCmd.Flags().BoolP("toggle", "t", false, "Help message for toggle")
	RootCmd.PersistentFlags().StringVarP(&uid, "uid", "U", "", "单据id")
	RootCmd.PersistentFlags().StringVarP(&rootID, "root_id", "R", "", "流程id")
	RootCmd.PersistentFlags().StringVarP(&nodeID, "node_id", "N", "", "节点id")
	RootCmd.PersistentFlags().StringVarP(&versionID, "version_id", "V", "", "运行版本id")
	RootCmd.PersistentFlags().StringVarP(&dataDir, "data_dir", "D", "",
		"数据保存路径,亦可通过环境变量 REDIS_DATA_DIR 指定")
	RootCmd.PersistentFlags().StringVarP(&backupDir, "backup_dir", "B", "",
		"备份保存路径,亦可通过环境变量REDIS_BACKUP_DIR指定")
	RootCmd.PersistentFlags().StringVarP(&payLoad, "payload", "p", "", "原子任务参数信息,base64包裹")
	RootCmd.PersistentFlags().StringVarP(&payLoadFormat, "payload-format", "m", "",
		"command payload format, default base64, value_allowed: base64|raw")
	RootCmd.PersistentFlags().StringVarP(&atomJobList, "atom-job-list", "A", "",
		"多个原子任务名用','分割,如 redis_install,redis_replicaof")
	RootCmd.PersistentFlags().StringVarP(&payLoadFile, "payload_file", "f", "", "原子任务参数信息,json文件")
	RootCmd.PersistentFlags().StringVarP(&user, "user", "u", "", "开启进程的os用户")
	RootCmd.PersistentFlags().StringVarP(&group, "group", "g", "", "开启进程的os用户属主")
	debugCmd.PersistentFlags().StringVarP(&printParamJson, "param", "P", "", "print atom job param")
	debugCmd.PersistentFlags().BoolVarP(&listJob, "list", "L", false, "list atom jobs")

	RootCmd.AddCommand(debugCmd)

}

func doPrintParamJson() {
	dir, _ := util.GetCurrentDirectory()
	if manager, err := jobmanager.NewJobGenericManager(uid, rootID, nodeID, versionID,
		payLoad, payLoadFormat, printParamJson, dir); err != nil {
		panic(err)
	} else {
		err = manager.LoadAtomJobs()
		if err != nil {
			fmt.Printf("err %s\n", err.Error())
			os.Exit(1)
		}
		r := manager.GetAtomJobInstance(printParamJson)
		fmt.Printf("%s\n", r.Param())
	}
	os.Exit(0)
}

// Execute adds all child commands to the root command and sets flags appropriately.
// This is called by main.main(). It only needs to happen once to the rootCmd.
func Execute() {
	err := RootCmd.Execute()
	if err != nil {
		os.Exit(1)
	}
}